import json

with open("updated-definition7.json", encoding="utf-8") as f:
    definition = json.load(f)

for node in definition["nodes"]:
    if node["name"] == "PlatformQuestionGenPrompt":
        for inp in node["inputs"]:
            if inp["name"] == "excerpts":
                inp["type"] = "Array"

with open("updated-definition8.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition8.json written successfully")