# Evaluation Observations

Ran `generate-eval-dataset.py` against `customer-request-flow` (flow ID: VJD7SPYVVH, alias: v1) with 3 test cases covering all three routing paths (bug report, platform question, other request). Uploaded results to Bedrock Evaluations using LLM-as-a-judge (Amazon Nova Pro) with the Builtin.Correctness metric.

**Result: 1.0 average correctness across all 3 tests.**

- Platform Question and Other Request paths performed as expected: the FAQ-answering prompt correctly cited the 30-day return policy, and the other-request prompt correctly redirected to phone support without hallucinating FAQ content.
- The Bug Report test also scored 1.0, but this reflects a lenient judge rather than a fully working path: the flow currently only returns the raw classifier label ("BUG_REPORT") for this branch, since the Bug Report Agent could not be built due to an AWS-side block (Bedrock Agents Classic entered maintenance mode for new agent creation as of July 30, 2026, affecting accounts without prior usage). Once the Agent is wired in, this response should be replaced with a proper ticket-confirmation message from the Agent, and the test suite should be re-run.
