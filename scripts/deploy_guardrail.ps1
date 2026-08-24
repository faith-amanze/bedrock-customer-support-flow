$env:PYTHONUTF8 = "1"
aws bedrock-agent update-flow --flow-identifier VJD7SPYVVH --name customer-request-flow --execution-role-arn arn:aws:iam::843794985908:role/service-role/AmazonBedrockExecutionRoleForFlows_Z8WDOV56XG8 --definition file://updated-definition3.json --region us-east-1 > update-guardrail-result.json

Write-Output "---prepared status---"
aws bedrock-agent prepare-flow --flow-identifier VJD7SPYVVH --region us-east-1
Start-Sleep -Seconds 10
aws bedrock-agent get-flow --flow-identifier VJD7SPYVVH --region us-east-1 --query 'status'