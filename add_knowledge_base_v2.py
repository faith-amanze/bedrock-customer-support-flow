import json

with open("updated-definition6.json", encoding="utf-8") as f:
    definition = json.load(f)

KB_ID = "P2VFMMWIHU"
GUARDRAIL_ID = "vn22c9cv3d7w"
GUARDRAIL_VERSION = "3"
PHONE_NUMBER = "1-800-555-0199"

# Fix the KB node: retrieval-only mode (no modelId), output as retrievalResults array
for node in definition["nodes"]:
    if node["name"] == "PlatformQuestionKB":
        node["outputs"] = [{"name": "retrievalResults", "type": "Array"}]
        node["configuration"]["knowledgeBase"] = {"knowledgeBaseId": KB_ID}

# Add a generation prompt node that takes retrieved chunks + the question
gen_prompt_text = (
    "You are a customer support assistant for an online shop. Below are retrieved "
    "FAQ excerpts that may or may not be relevant to the customer's question. "
    "If the excerpts clearly answer the question, give a clear, friendly answer "
    "based on them. If they don't contain a relevant answer, do not guess -- "
    "respond with exactly: \"I'm sorry, I don't have information on that. Please "
    f"call our support line at {PHONE_NUMBER} for further help.\"\n\n"
    "Retrieved excerpts:\n{{excerpts}}\n\nCustomer question: {{question}}"
)

gen_node = {
    "name": "PlatformQuestionGenPrompt",
    "type": "Prompt",
    "configuration": {
        "prompt": {
            "sourceConfiguration": {
                "inline": {
                    "templateType": "TEXT",
                    "templateConfiguration": {
                        "text": {
                            "text": gen_prompt_text,
                            "inputVariables": [{"name": "excerpts"}, {"name": "question"}]
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
        {"name": "excerpts", "type": "String", "expression": "$.data"},
        {"name": "question", "type": "String", "expression": "$.data"}
    ],
    "outputs": [{"name": "modelCompletion", "type": "String"}]
}
definition["nodes"].append(gen_node)

# Fix connections: KB output goes to the new gen prompt, not directly to Output
definition["connections"] = [
    c for c in definition["connections"] if c["name"] != "PlatformQuestionKBToOutput"
]

definition["connections"] += [
    {"type": "Data", "name": "KBToGenPromptExcerpts", "source": "PlatformQuestionKB", "target": "PlatformQuestionGenPrompt",
     "configuration": {"data": {"sourceOutput": "retrievalResults", "targetInput": "excerpts"}}},
    {"type": "Data", "name": "FlowInputToGenPromptQuestion", "source": "FlowInputNode", "target": "PlatformQuestionGenPrompt",
     "configuration": {"data": {"sourceOutput": "document", "targetInput": "question"}}},
    {"type": "Data", "name": "GenPromptToOutput", "source": "PlatformQuestionGenPrompt", "target": "PlatformQuestionOutput",
     "configuration": {"data": {"sourceOutput": "modelCompletion", "targetInput": "document"}}},
]

with open("updated-definition7.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition7.json written successfully")