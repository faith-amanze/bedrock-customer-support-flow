import json

with open("flow-definition-latest.json", encoding="utf-16") as f:
    data = json.load(f)

definition = data["definition"]

GUARDRAIL_ID = "vn22c9cv3d7w"
GUARDRAIL_VERSION = "1"

prompt_node_names = {"ClassifierPrompt", "PlatformQuestionPrompt", "OtherRequestPrompt"}

for node in definition["nodes"]:
    if node["name"] in prompt_node_names:
        node["configuration"]["prompt"]["guardrailConfiguration"] = {
            "guardrailIdentifier": GUARDRAIL_ID,
            "guardrailVersion": GUARDRAIL_VERSION
        }

with open("updated-definition3.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition3.json written successfully")