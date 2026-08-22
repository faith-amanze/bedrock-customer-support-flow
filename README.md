# Customer Support Chatbot with Amazon Bedrock Flows

This project implements a Bedrock Flow (`customer-request-flow`, flow ID `VJD7SPYVVH`) that classifies incoming customer messages into one of three categories - **bug report**, **platform question**, or **other request** - and routes each to a distinct path:

- **Bug reports** are acknowledged by a dedicated prompt node that confirms a ticket was created and asks follow-up questions (steps to reproduce, browser/OS/device) when those details are missing.
- **Platform questions** are answered using a Bedrock Knowledge Base built from the FAQ document, with a fallback to a support phone number when the question isn't covered.
- **Other requests** are redirected to a support phone number.

All three paths are also protected by a Bedrock Guardrail filtering harmful content, and a Lambda tool (`create_bug_report.py`) that writes bug reports to a DynamoDB table was built and verified independently (see Known Limitation below for why it isn't yet wired into the flow's live response).

The flow was tested with an automated test suite (`flow-tests.json`, 7 cases covering all 3 paths plus edge cases: ambiguous message, very short message, uncovered FAQ question, prompt injection attempt) and evaluated using Bedrock Evaluations (LLM-as-a-judge).

**Final result: 1.00 average correctness across all 7 tests** (job: flow-eval-run-final).

Full details and evaluation notes: [README_evaluation.md](./README_evaluation.md)

## Known limitation: Bedrock Agent / automatic ticket creation

The bug report path was originally designed to use a **Bedrock Agent** to collect information conversationally and invoke the Lambda tool to create the ticket automatically. This could not be wired into the flow because **Bedrock Agents Classic closed to new customers on July 30, 2026**, and this AWS account has no prior agent usage, so `CreateAgent` returns `AccessDeniedException` (reproducible via CLI; confirmed on two different AWS accounts across this project).

- The Lambda tool itself (`create_bug_report.py`) works correctly and was tested directly - see `response2.json` and `screenshots/06-dynamodb-bug-report-record.png` for a successfully created ticket in DynamoDB.
- As a substitute that doesn't require the blocked Agent, the flow now includes a `BugReportPrompt` node that produces a realistic, helpful acknowledgment message directly from the classifier's output. This does not call the Lambda tool as part of the flow itself - that connection would require the Agent (or an equivalent Lambda-invoking mechanism) that this account cannot currently provision.
- Console evidence of the platform-level Agent block: `screenshots/agents-classic-maintenance-mode.png` and `screenshots/05-bug-report-agent-blocked.png`.

## Rubric evidence map

| Rubric requirement | Evidence |
|---|---|
| Full flow diagram | `screenshots/01-full-flow-diagram.png` |
| Classifier prompt configuration | `screenshots/02-classifier-prompt-config.png` |
| Condition node expressions | `screenshots/03-condition-node-expressions.png` |
| Agent node config / action group | Blocked - see Known Limitation above. Evidence: `screenshots/05-bug-report-agent-blocked.png`, `screenshots/agents-classic-maintenance-mode.png` |
| Flow test - bug report creation | `screenshots/07-flow-test-bug-report.png` |
| Flow test - bug report with follow-up questions | `screenshots/08-flow-test-bug-report-followup.png` |
| DynamoDB BugReports record | `screenshots/06-dynamodb-bug-report-record.png` |
| FAQ Knowledge Base config + generation prompt | `screenshots/04-faq-knowledge-base-config.png` |
| Flow test - covered FAQ question | `screenshots/09-flow-test-faq-covered.png` |
| Flow test - uncovered FAQ question | `screenshots/10-flow-test-faq-uncovered.png` |
| Flow test - other request | `screenshots/11-flow-test-other-request.png` |
| `flow-tests.json` | [flow-tests.json](./flow-tests.json) |
| Evaluation JSONL output | [output_eval_dataset.jsonl](./output_eval_dataset.jsonl), [eval-results-final.jsonl](./eval-results-final.jsonl) |
| Bedrock Evaluation job results page | `screenshots/12-bedrock-evaluation-results.png` |
| Written observation | [README_evaluation.md](./README_evaluation.md) |

## Stand-out additions

- **Guardrail**: `customer-support-guardrail` (ID `vn22c9cv3d7w`) attached to all Prompt nodes, filtering sexual, violent, hateful, insulting, and misconduct content. See `README_evaluation.md` for a documented finding on why the `PROMPT_ATTACK` filter was disabled (false positives on the flow's own instruction-style prompts) and how prompt-injection resistance is achieved instead.
- **Knowledge Base instead of embedded FAQ**: the Platform Question path retrieves from a Bedrock Knowledge Base (`faq-knowledge-base`, ID `P2VFMMWIHU`) built from `online_shop_faq.md`, rather than embedding the full FAQ text in every prompt.
- **Edge-case tests**: `flow-tests.json` includes an ambiguous message, a very short message, an uncovered FAQ question, and a prompt-injection attempt, in addition to the three baseline path tests.
- Structured output for the classifier (JSON-schema-constrained decoding) was investigated but is not currently supported by Bedrock Flows' Prompt node configuration (confirmed via the `PromptFlowNodeConfiguration` API schema, which only exposes `sourceConfiguration` and `guardrailConfiguration`). Strict prompt instructions are used instead, verified reliable across all test runs.

## Repo structure

- `flow-definition*.json`, `updated-definition*.json`, `current-flow-full.json` - flow configuration exports at various stages
- `online_shop_faq.md` - FAQ content, source document for the Knowledge Base
- `create_bug_report.py` - Lambda tool for creating bug report tickets
- `add_prompt.py`, `add_guardrail.py`, `add_knowledge_base*.py`, `add_bugreport_prompt.py` - scripts used to build up the flow definition programmatically
- `generate-eval-dataset.py`, `flow-tests.json`, `output_eval_dataset.jsonl`, `eval-results-final.jsonl` - testing and evaluation
- `cloudformation-*.yaml` - infrastructure definitions (Lambda + DynamoDB, evaluation S3/IAM resources)
- `screenshots/` - all evidence screenshots referenced above
- `README_evaluation.md` - detailed evaluation results, the guardrail finding, and the Agent limitation writeup
