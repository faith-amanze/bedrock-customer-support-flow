import json

with open("updated-definition.json") as f:
    definition = json.load(f)

with open("online_shop_faq.md", encoding="utf-8") as f:    faq_text = f.read()

PHONE_NUMBER = "1-800-555-0199"

platform_question_prompt_text = (
    "You are a customer support assistant for an online shop. Answer the "
    "customer's question using ONLY the information in the FAQ below. If the "
    "question is clearly covered by one of the FAQ entries, give a clear, "
    "friendly answer based on that entry. If the question is NOT covered by "
    "the FAQ, do not guess -- instead respond with exactly: \"I'm sorry, I "
    f"don't have information on that. Please call our support line at {PHONE_NUMBER} "
    "for further help.\"\n\nFAQ:\n" + faq_text +
    "\n\nCustomer question: {{question}}"
)

other_request_prompt_text = (
    "You are a customer support assistant. The customer's message doesn't "
    "relate to a bug report or a question covered by our FAQ. Politely let "
    "them know a member of our support team can help, and direct them to "
    f"call {PHONE_NUMBER}. Keep the response short and friendly. Do not ask "
    "follow-up questions.\n\nCustomer message: {{question}}"
)

def make_prompt_node(name, text):
    return {
        "name": name,
        "type": "Prompt",
        "configuration": {
            "prompt": {
                "sourceConfiguration": {
                    "inline": {
                        "templateType": "TEXT",
                        "templateConfiguration": {
                            "text": {
                                "text": text,
                                "inputVariables": [{"name": "question"}]
                            }
                        },
                        "modelId": "amazon.nova-pro-v1:0",
                        "inferenceConfiguration": {
                            "text": {
                                "temperature": 0.7,
                                "topP": 1.0,
                                "maxTokens": 512,
                                "stopSequences": []
                            }
                        }
                    }
                }
            }
        },
        "inputs": [{"name": "question", "type": "String", "expression": "$.data"}],
        "outputs": [{"name": "modelCompletion", "type": "String"}]
    }

definition["nodes"].append(make_prompt_node("PlatformQuestionPrompt", platform_question_prompt_text))
definition["nodes"].append(make_prompt_node("OtherRequestPrompt", other_request_prompt_text))

connections = [c for c in definition["connections"] if c["target"] not in ("PlatformQuestionOutput", "OtherRequestOutput")]

connections += [
    {"type": "Data", "name": "FlowInputToPlatformQuestionPrompt", "source": "FlowInputNode", "target": "PlatformQuestionPrompt",
     "configuration": {"data": {"sourceOutput": "document", "targetInput": "question"}}},
    {"type": "Conditional", "name": "ConditionToPlatformQuestionPrompt", "source": "ConditionNode_1", "target": "PlatformQuestionPrompt",
     "configuration": {"conditional": {"condition": "PlatformQuestion"}}},
    {"type": "Data", "name": "PlatformQuestionPromptToOutput", "source": "PlatformQuestionPrompt", "target": "PlatformQuestionOutput",
     "configuration": {"data": {"sourceOutput": "modelCompletion", "targetInput": "document"}}},

    {"type": "Data", "name": "FlowInputToOtherRequestPrompt", "source": "FlowInputNode", "target": "OtherRequestPrompt",
     "configuration": {"data": {"sourceOutput": "document", "targetInput": "question"}}},
    {"type": "Conditional", "name": "ConditionToOtherRequestPrompt", "source": "ConditionNode_1", "target": "OtherRequestPrompt",
     "configuration": {"conditional": {"condition": "OtherRequest"}}},
    {"type": "Data", "name": "OtherRequestPromptToOutput", "source": "OtherRequestPrompt", "target": "OtherRequestOutput",
     "configuration": {"data": {"sourceOutput": "modelCompletion", "targetInput": "document"}}},
]

definition["connections"] = connections

with open("updated-definition2.json", "w") as f:
    json.dump(definition, f, indent=2)

print("updated-definition2.json written successfully")