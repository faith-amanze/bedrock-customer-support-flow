# Customer Support Chatbot with Amazon Bedrock Flows

This project implements a Bedrock Flow (`customer-request-flow`, flow ID `VJD7SPYVVH`) that classifies incoming customer messages into one of three categories — **bug report**, **platform question**, or **other request** — and routes each to a distinct path:

- **Bug reports** are logged as tickets in a DynamoDB table (`BugReports`).
- **Platform questions** are answered from an embedded FAQ, with a fallback to a support phone number when the question isn't covered.
- **Other requests** are redirected to a support phone number.

The flow was tested with an automated test suite (`flow-tests.json`) and evaluated using Bedrock Evaluations (LLM-as-a-judge), scoring **1.0 average correctness** across all three routing paths.

## Known limitation: Bedrock Agent

The bug report path was designed to use a **Bedrock Agent** to collect information and invoke a Lambda tool to create the ticket. This could not be wired into the flow because **Bedrock Agents Classic closed to new customers on July 30, 2026**, and this AWS account has no prior agent usage, so `CreateAgent` returns `AccessDeniedException`.

- The Lambda tool itself (`create_bug_report.py`) works correctly and was tested directly — see `response2.json` and `screenshots/06-dynamodb-bug-report-record.png` for a successfully created ticket in DynamoDB.
- The flow's bug report path currently returns the raw classifier label rather than an agent-generated confirmation, since no agent could be attached to the flow.
- Console evidence of this platform-level block: `screenshots/agents-classic-maintenance-mode.png` (Agents Classic showing 0 agents and the maintenance-mode banner) and `screenshots/05-bug-report-agent-blocked.png` (CLI `AccessDeniedException`).

Full details and evaluation notes: [`README_evaluation.md`](./README_evaluation.md)

## Rubric evidence map

| Rubric requirement | Evidence |
|---|---|
| Full flow diagram | `screenshots/01-full-flow-diagram.png` |
| Classifier prompt configuration | `screenshots/02-classifier-prompt-config.png` |
| Condition node expressions | `screenshots/03-condition-node-expressions.png` |
| Agent node config / action group | `screenshots/05-bug-report-agent-blocked.png`, `screenshots/agents-classic-maintenance-mode.png` (blocked — see Known Limitation above) |
| Flow test — bug report creation | `screenshots/07-flow-test-bug-report.png` |
| Flow test — bug report with follow-up | Not available — blocked by the same Agent limitation |
| DynamoDB BugReports record | `screenshots/06-dynamodb-bug-report-record.png` |
| FAQ prompt embedded content | `screenshots/04-faq-prompt-embedded-content.png` |
| Flow test — covered FAQ question | `screenshots/09-flow-test-faq-covered.png` |
| Flow test — uncovered FAQ question | `screenshots/10-flow-test-faq-uncovered.png` |
| Flow test — other request | `screenshots/11-flow-test-other-request.png` |
| `flow-tests.json` | [`flow-tests.json`](./flow-tests.json) |
| Evaluation JSONL output | [`output_eval_dataset.jsonl`](./output_eval_dataset.jsonl), [`eval-results.jsonl`](./eval-results.jsonl) |
| Bedrock Evaluation job results page | `screenshots/12-bedrock-evaluation-results.png` |
| Written observation | [`README_evaluation.md`](./README_evaluation.md) |

## Repo structure

- `flow-definition.json`, `updated-definition*.json` — flow configuration exports
- `online_shop_faq.md` — FAQ content embedded in the Platform Question prompt
- `create_bug_report.py`, `add_prompt.py` — Lambda / setup scripts
- `generate-eval-dataset.py`, `flow-tests.json`, `output_eval_dataset.jsonl`, `eval-results.jsonl` — testing and evaluation
- `cloudformation-*.yaml` — infrastructure definitions
- `screenshots/` — all evidence screenshots referenced above
- `README_evaluation.md` — detailed evaluation results and the Agent limitation writeup
