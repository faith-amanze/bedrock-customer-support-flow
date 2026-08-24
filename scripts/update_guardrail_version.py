import json

with open("updated-definition3.json", encoding="utf-8") as f:
    definition = json.load(f)

for node in definition["nodes"]:
    if node["type"] == "Prompt" and "guardrailConfiguration" in node["configuration"]["prompt"]:
        node["configuration"]["prompt"]["guardrailConfiguration"]["guardrailVersion"] = "2"

with open("updated-definition4.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition4.json written successfully")