import boto3

# SQS Service
QUEUE_NAME = 'cw-sqs-1703130'
# S3 Service
BUCKET_NAME = 'cw-bucket-1703130'
# CloudFormation
STACK_NAME = 'cw-cloudformation-1703130'
# DynamoDB Service
DDB_TABLE = 'cw-ddb-1703130'
# EventBridge Service
TRANSCRIPTION_EVENTBRIDGE_RULE = 'cw-transcription-finish-1703130'
# Lambda Service
LAMBDA_NAME = 'cw-analyze-sentiment-1703130'
LAMBDA_ZIP = './lambda/src.zip'

# IAM
LAMBDA_POLICY_NAME = 'cw-lambda-policy-1703130'
LAMBDA_ROLE_NAME = 'cw-lambda-role-1703130'

# Account
client = boto3.client("sts")
identity = client.get_caller_identity()

ACCOUNT_ID = identity['Account']
REGION = 'eu-west-2'