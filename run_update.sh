aws bedrock-agent update-flow \
  --flow-identifier VJD7SPYVVH \
  --name customer-request-flow \
  --execution-role-arn arn:aws:iam::843794985908:role/service-role/AmazonBedrockExecutionRoleForFlows_Z8WDOV56XG8 \
  --definition file://updated-definition.json \
  --region us-east-1 > update-result.json

cat update-result.json | python3 -m json.tool | head -10