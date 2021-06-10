import boto3
from botocore.exceptions import ClientError

import constants

def delete_sqs():
  print(f'\nDeleting SQS queue: {constants.QUEUE_NAME}')
  sqs_client = boto3.client('sqs')
  try:    
    queue = sqs_client.get_queue_url(QueueName=constants.QUEUE_NAME)
    sqs_client.delete_queue(QueueUrl=queue['QueueUrl'])
    print(f'SQS Queue "{constants.QUEUE_NAME}" deleted successfully')
  except ClientError as e:
    print(e)

def delete_bucket():
  print(f'\nDeleting S3 bucket: {constants.BUCKET_NAME}')
  s3_client = boto3.client('s3', region_name=constants.REGION)
  s3_resource = boto3.resource('s3', region_name=constants.REGION)
  try:   
    bucket = s3_resource.Bucket(constants.BUCKET_NAME)
    bucket.objects.all().delete()
    s3_client.delete_bucket(Bucket=constants.BUCKET_NAME)
    print(f'Bucket "{constants.BUCKET_NAME}" deleted successfully')
  except ClientError as e:
    print(e)

def delete_stack():
  print(f'\nDeleting CloudFormation stack: {constants.STACK_NAME}')
  cf_client = boto3.client('cloudformation')
  try:    
    cf_client.delete_stack(StackName=constants.STACK_NAME)
    print(f'Stack "{constants.STACK_NAME}" deleted successfully')
  except ClientError as e:
    print(e)

def delete_lambda():
  print(f'\nDeleting Lambda function: {constants.LAMBDA_NAME}')
  lambda_client = boto3.client('lambda')
  try:    
    lambda_client.delete_function(FunctionName=constants.LAMBDA_NAME)
    print(f'Lambda function "{constants.LAMBDA_NAME}" deleted successfully')
  except ClientError as e:
    print(e)

  try:
    events = lambda_client.list_event_source_mappings(
      EventSourceArn=f'arn:aws:sqs:{constants.REGION}:{constants.ACCOUNT_ID}:{constants.QUEUE_NAME}',
      FunctionName=constants.LAMBDA_NAME
    )
    for event in events['EventSourceMappings']:
      lambda_client.delete_event_source_mapping(UUID=event['UUID'])
    print(f'Lambda function "{constants.LAMBDA_NAME}" event source mappings deleted successfully')
  except ClientError as e:
    print(e)

def delete_lambda_iam():
  print(f'\nDeleting IAM role: {constants.LAMBDA_ROLE_NAME}')
  iam_client = boto3.client('iam')
  policy_arn = f'arn:aws:iam::{constants.ACCOUNT_ID}:policy/{constants.LAMBDA_POLICY_NAME}'
  try:
    iam_client.detach_role_policy(
      RoleName=constants.LAMBDA_ROLE_NAME,
      PolicyArn=policy_arn
    )
    print(f'IAM policy "{constants.LAMBDA_POLICY_NAME}" successfully detached from the IAM role "{constants.LAMBDA_ROLE_NAME}"')

    policy_versions = iam_client.list_policy_versions(PolicyArn=policy_arn)
    for version in policy_versions['Versions']:
      if version['IsDefaultVersion']:
        continue
      iam_client.delete_policy_version(
        PolicyArn=policy_arn,
        VersionId=version['VersionId']
      )
    print(f'IAM policy "{constants.LAMBDA_POLICY_NAME}" versions deleted successfully')

    iam_client.delete_policy(PolicyArn=policy_arn)
    print(f'IAM policy "{constants.LAMBDA_POLICY_NAME}" deleted successfully')

    iam_client.delete_role(RoleName=constants.LAMBDA_ROLE_NAME)
    print(f'IAM role "{constants.LAMBDA_ROLE_NAME}" deleted successfully')
  except ClientError as e:
    print(e)

def delete_eventbridge_rule():
  print(f'\nDeleting EventBridge rule: {constants.TRANSCRIPTION_EVENTBRIDGE_RULE}')
  eb_client = boto3.client('events')
  try:
    event_targets = eb_client.list_targets_by_rule(Rule=constants.TRANSCRIPTION_EVENTBRIDGE_RULE)
    target_ids = [target['Id'] for target in event_targets['Targets']]
    eb_client.remove_targets(
      Rule=constants.TRANSCRIPTION_EVENTBRIDGE_RULE,
      Ids=target_ids
    )
    print(f'EventBridge rule "{constants.TRANSCRIPTION_EVENTBRIDGE_RULE}" targets removed successfully')

    eb_client.delete_rule(Name=constants.TRANSCRIPTION_EVENTBRIDGE_RULE)
    print(f'EventBridge rule "{constants.TRANSCRIPTION_EVENTBRIDGE_RULE}" deleted successfully')
  except ClientError as e:
    print(e)