import json

with open("updated-definition5.json", encoding="utf-8") as f:
    definition = json.load(f)

KB_ID = "P2VFMMWIHU"
GUARDRAIL_ID = "vn22c9cv3d7w"
GUARDRAIL_VERSION = "3"

# Remove the old PlatformQuestionPrompt node
definition["nodes"] = [n for n in definition["nodes"] if n["name"] != "PlatformQuestionPrompt"]

# Add the new KnowledgeBase node
kb_node = {
    "name": "PlatformQuestionKB",
    "type": "KnowledgeBase",
    "inputs": [
        {"name": "retrievalQuery", "type": "String", "expression": "$.data"}
    ],
    "outputs": [
        {"name": "outputText", "type": "String"}
    ],
    "configuration": {
        "knowledgeBase": {
            "knowledgeBaseId": KB_ID,
            "modelId": "amazon.nova-pro-v1:0",
            "guardrailConfiguration": {
                "guardrailIdentifier": GUARDRAIL_ID,
                "guardrailVersion": GUARDRAIL_VERSION
            }
        }
    }
}
definition["nodes"].append(kb_node)

# Remove old connections referencing PlatformQuestionPrompt
definition["connections"] = [
    c for c in definition["connections"]
    if c["source"] != "PlatformQuestionPrompt" and c["target"] != "PlatformQuestionPrompt"
]

# Add new connections for the KB node
definition["connections"] += [
    {"type": "Data", "name": "FlowInputToPlatformQuestionKB", "source": "FlowInputNode", "target": "PlatformQuestionKB",
     "configuration": {"data": {"sourceOutput": "document", "targetInput": "retrievalQuery"}}},
    {"type": "Conditional", "name": "ConditionToPlatformQuestionKB", "source": "ConditionNode_1", "target": "PlatformQuestionKB",
     "configuration": {"conditional": {"condition": "PlatformQuestion"}}},
    {"type": "Data", "name": "PlatformQuestionKBToOutput", "source": "PlatformQuestionKB", "target": "PlatformQuestionOutput",
     "configuration": {"data": {"sourceOutput": "outputText", "targetInput": "document"}}},
]

with open("updated-definition6.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition6.json written successfully")