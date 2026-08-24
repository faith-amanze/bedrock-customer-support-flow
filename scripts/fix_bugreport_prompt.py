import json

with open("updated-definition-bugreport.json", encoding="utf-8") as f:
    definition = json.load(f)

new_text = (
    "You are a customer support assistant. The customer has reported a bug. "
    "Acknowledge their report warmly, confirm that a support ticket has been "
    "created, and let them know the team will follow up. If the customer's "
    "message is missing helpful detail (like the steps to reproduce the issue "
    "or their browser/OS/device), politely ask them to share those details so "
    "the team can investigate faster. Do not invent a ticket number -- refer "
    "to it generically as 'your ticket'. Keep the response to 2-3 short "
    "sentences. Do not include a sign-off, signature, or placeholder name."
    "\n\nCustomer message: {{message}}"
)

for node in definition["nodes"]:
    if node["name"] == "BugReportPrompt":
        node["configuration"]["prompt"]["sourceConfiguration"]["inline"]["templateConfiguration"]["text"]["text"] = new_text

with open("updated-definition-bugreport2.json", "w", encoding="utf-8") as f:
    json.dump(definition, f, indent=2)

print("updated-definition-bugreport2.json written successfully")