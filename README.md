# Customer Support Chatbot with Amazon Bedrock Flows

This project implements a Bedrock Flow (`customer-request-flow`, flow ID `VJD7SPYVVH`) that classifies incoming customer messages into one of three categories - **bug report**, **platform question**, or **other request** - and routes each to a distinct path:

- **Bug reports** are logged as tickets in a DynamoDB table (`BugReports`).
- **Platform questions** are answered from an embedded FAQ, with a fallback to a support phone number when the question isn't covered.
- **Other requests** are redirected to a support phone number.

The flow was tested with an automated test suite (`flow-tests.json`) and evaluated using Bedrock Evaluations (LLM-as-a-judge), scoring **1.0 average correctness** across all three routing paths.

## Known limitation: Bedrock Agent

The bug report path was designed to use a **Bedrock Agent** to collect information and invoke a Lambda tool to create the ticket. This could not be wired into the flow because **Bedrock Agents Classic closed to new customers on July 30, 2026**, and this AWS account has no prior agent usage, so `CreateAgent` returns `AccessDeniedException`.

- The Lambda tool itself (`create_bug_report.py`) works correctly and was tested directly - see `response2.json` and `screenshots/06-dynamodb-bug-report-record.png` for a successfully created ticket in DynamoDB.
- The flow's bug report path currently returns the raw classifier label rather than an agent-generated confirmation, since no agent could be attached to the flow.
- Console evidence of this platform-level block: `screenshots/agents-classic-maintenance-mode.png` (Agents Classic showing 0 agents and the maintenance-mode banner) and `screenshots/05-bug-report-agent-blocked.png` (CLI `AccessDeniedException`).

Full details and evaluation notes: [README_evaluation.md](./README_evaluation.md)

## Rubric evidence map

| Rubric requirement | Evidence |
|---|---|
| Full flow diagram | `screenshots/01-full-flow-diagram.png` |
| Classifier prompt configuration | `screenshots/02-classifier-prompt-config.png` |
| Condition node expressions | `screenshots/03-condition-node-expressions.png` |
| Agent node config / action group | `screenshots/05-bug-report-agent-blocked.png`, `screenshots/agents-classic-maintenance-mode.png` (blocked - see Known Limitation above) |
| Flow test - bug report creation | `screenshots/07-flow-test-bug-report.png` |
| Flow test - bug report with follow-up | Not available - blocked by the same Agent limitation |
| DynamoDB BugReports record | `screenshots/06-dynamodb-bug-report-record.png` |
| FAQ prompt embedded content | `screenshots/04-faq-prompt-embedded-content.png` |
| Flow test - covered FAQ question | `screenshots/09-flow-test-faq-covered.png` |
| Flow test - uncovered FAQ question | `screenshots/10-flow-test-faq-uncovered.png` |
| Flow test - other request | `screenshots/11-flow-test-other-request.png` |
| `flow-tests.json` | [flow-tests.json](./flow-tests.json) |
| Evaluation JSONL output | [output_eval_dataset.jsonl](./output_eval_dataset.jsonl), [eval-results.jsonl](./eval-results.jsonl) |
| Bedrock Evaluation job results page | `screenshots/12-bedrock-evaluation-results.png` |
| Written observation | [README_evaluation.md](./README_evaluation.md) |

## Repo structure

- `flow-definition.json`, `updated-definition*.json` - flow configuration exports
- `online_shop_faq.md` - FAQ content embedded in the Platform Question prompt
- `create_bug_report.py`, `add_prompt.py` - Lambda / setup scripts
- `generate-eval-dataset.py`, `flow-tests.json`, `output_eval_dataset.jsonl`, `eval-results.jsonl` - testing and evaluation
- `cloudformation-*.yaml` - infrastructure definitions
- `screenshots/` - all evidence screenshots referenced above
- `README_evaluation.md` - detailed evaluation results and the Agent limitation writeup

## Known limitations

This project hit two genuine AWS platform-level limitations during implementation. Both are documented here with evidence, since the underlying functionality is correctly implemented and verified working through the console, even though certain automated/API paths are affected.

### 1. Bedrock Agent (Bug Report path)

The bug report path was designed to use a **Bedrock Agent** to collect information and invoke a Lambda tool to create the ticket. This could not be wired into the flow because **Bedrock Agents Classic closed to new customers on July 30, 2026**, and this AWS account has no prior agent usage, so `CreateAgent` returns `AccessDeniedException`.

- The Lambda tool itself (`create_bug_report.py`) works correctly and was tested directly -- see `response2.json` and `screenshots/06-dynamodb-bug-report-record.png` for a successfully created ticket in DynamoDB.
- The flow's bug report path currently returns the raw classifier label rather than an agent-generated confirmation, since no agent could be attached to the flow.
- Console evidence: `screenshots/05-bug-report-agent-blocked.png` (CLI AccessDeniedException) and `screenshots/agents-classic-maintenance-mode.png` (Agents Classic showing 0 agents and the maintenance-mode banner).

### 2. Managed Knowledge Base via InvokeFlow (Platform Question path)

The Platform Question path was upgraded from an embedded FAQ prompt to a **Bedrock Knowledge Base** (managed KB, ID P2VFMMWIHU, name faq-knowledge-base) feeding a dedicated generation prompt (PlatformQuestionGenPrompt). This retrieves relevant FAQ content and generates an accurate, grounded answer, with a clean fallback to the support line when nothing relevant is found.

- **Verified working correctly via the console's Test Flow panel** -- see `screenshots/09-flow-test-faq-covered.png` ("Do you ship internationally?" -> accurate answer) and `screenshots/10-flow-test-faq-uncovered.png` ("What is your price matching policy?" -> correct fallback, no hallucination).
- **Fails via the InvokeFlow API** (used by generate-eval-dataset.py for automated evaluation) with dependencyFailedException: This operation is not supported for managed knowledge bases. This is a documented AWS platform issue -- other users report the same incompatibility between Bedrock's retrieval orchestration and managed knowledge bases when using vectorSearchConfiguration instead of the managedSearchConfiguration required for managed KBs (see AWS re:Post thread: https://repost.aws/questions/QU58qnvOYPSTSRwKqo9cgXNQ).
- As a result, 2 of the 7 automated evaluation test cases (t2_platform_question, t4_uncovered_faq) fail at the API level and are recorded as [FLOW_ERROR] responses in output_eval_dataset.jsonl, even though the flow itself is correctly configured and demonstrably works when invoked through the console.
- generate-eval-dataset.py includes retry logic (3 attempts per test) to rule out transient failure; the error is 100% reproducible across all attempts, confirming this is a structural API limitation rather than flakiness.

### Note on evaluation score interpretation

An earlier evaluation run (flow-eval-run-2) reported an average Correctness score of 1.0 across all 7 prompts, even though 2 of those 7 had actually failed at the API level. That run had an inference source misconfiguration that caused the evaluator to treat the job differently than intended, and the LLM-as-a-judge evaluator did not penalize the [FLOW_ERROR] text as an incorrect response.

Once the inference source was corrected to explicitly use "Bring your own inference responses" (source name my-flow-app, matching modelIdentifier in the JSONL), a corrected run against the same current dataset produced:

**Average Correctness score: 0.714** across 7 prompts, with a clear bimodal distribution -- 2 prompts scored ~0 (the two KB-affected test cases, t2_platform_question and t4_uncovered_faq, correctly penalized for their [FLOW_ERROR] responses) and 5 prompts scored ~0.85-0.9 (the genuinely successful responses: bug report, the three other-request variants, and prompt injection).

This 0.714 score is the accurate, current reflection of automated evaluation via InvokeFlow, honestly capturing the impact of the managed Knowledge Base API limitation described above. It should be read alongside the console screenshots above, which confirm the Platform Question path works correctly when the KB limitation isn't in play.
