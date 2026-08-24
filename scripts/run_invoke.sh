aws bedrock-agent-runtime start-flow-execution \
  --flow-identifier VJD7SPYVVH \
  --flow-alias-identifier TSTALIASID \
  --flow-execution-name test-run-3 \
  --inputs file://invoke_input.json \
  --region us-east-1

echo "---waiting---"
sleep 8
echo "---checking events---"
aws bedrock-agent-runtime list-flow-execution-events \
  --flow-identifier VJD7SPYVVH \
  --flow-alias-identifier TSTALIASID \
  --execution-identifier test-run-3 \
  --event-type Node \
  --region us-east-1