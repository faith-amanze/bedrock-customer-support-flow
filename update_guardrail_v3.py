import json

with open("updated-definition4.json", encoding="utf-8") as f:
    definition = json.load(f)

for node in definition["nodes"]:
    if node["type"] == "Prompt" and "guardrailConfiguration" in node["configuration"]["prompt"]:
        node["configuration"]["prompt"]["guardrailConfiguration"]["guardrailVersion"] = "3"

with open("updated-definition5.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition5.json written successfully")