import json

with open("flow-definition-current.json", encoding="utf-16") as f:
    data = json.load(f)

definition = data["definition"]

GUARDRAIL_ID = "vn22c9cv3d7w"
GUARDRAIL_VERSION = "3"

bug_report_prompt_text = (
    "You are a customer support assistant. The customer has reported a bug. "
    "Acknowledge their report warmly, confirm that a support ticket has been "
    "created, and let them know the team will follow up. If the customer's "
    "message is missing helpful detail (like the steps to reproduce the issue "
    "or their browser/OS/device), politely ask them to share those details so "
    "the team can investigate faster. Do not invent a ticket number -- refer "
    "to it generically as 'your ticket'. Keep the response short and friendly."
    "\n\nCustomer message: {{message}}"
)

bug_report_node = {
    "name": "BugReportPrompt",
    "type": "Prompt",
    "configuration": {
        "prompt": {
            "sourceConfiguration": {
                "inline": {
                    "templateType": "TEXT",
                    "templateConfiguration": {
                        "text": {
                            "text": bug_report_prompt_text,
                            "inputVariables": [{"name": "message"}]
                        }
                    },
                    "modelId": "amazon.nova-pro-v1:0",
                    "inferenceConfiguration": {
                        "text": {"temperature": 0.7, "topP": 1.0, "maxTokens": 512, "stopSequences": []}
                    }
                }
            },
            "guardrailConfiguration": {
                "guardrailIdentifier": GUARDRAIL_ID,
                "guardrailVersion": GUARDRAIL_VERSION
            }
        }
    },
    "inputs": [
        {"name": "message", "type": "String", "expression": "$.data"}
    ],
    "outputs": [
        {"name": "modelCompletion", "type": "String"}
    ]
}
definition["nodes"].append(bug_report_node)

# Remove old connections directly targeting BugReportOutput
definition["connections"] = [
    c for c in definition["connections"] if c["target"] != "BugReportOutput"
]

# Add new connections: FlowInput -> BugReportPrompt, Condition -> BugReportPrompt, BugReportPrompt -> BugReportOutput
definition["connections"] += [
    {"type": "Data", "name": "FlowInputToBugReportPrompt", "source": "FlowInputNode", "target": "BugReportPrompt",
     "configuration": {"data": {"sourceOutput": "document", "targetInput": "message"}}},
    {"type": "Conditional", "name": "ConditionToBugReportPrompt", "source": "ConditionNode_1", "target": "BugReportPrompt",
     "configuration": {"conditional": {"condition": "BugReport"}}},
    {"type": "Data", "name": "BugReportPromptToOutput", "source": "BugReportPrompt", "target": "BugReportOutput",
     "configuration": {"data": {"sourceOutput": "modelCompletion", "targetInput": "document"}}},
]

with open("updated-definition-bugreport.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition-bugreport.json written successfully")