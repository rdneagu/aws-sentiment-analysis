import boto3, json, os
from botocore.exceptions import ClientError

from zipfile import ZipFile

import iam.lambda_policy, iam.sqs_policy
import constants

def zip_lambda_function():
  with ZipFile(constants.LAMBDA_ZIP, 'w') as zipfile:
    for file in os.listdir('lambda/src'):
      file_path = os.path.join(os.getcwd(), 'lambda', 'src', file)
      zipfile.write(file_path, file)

def create_sqs():
  print(f'\nCreating SQS queue: {constants.QUEUE_NAME}')
  sqs_client = boto3.client('sqs')
  sqs_resource = boto3.resource('sqs')
  try:
    sqs_client.create_queue(QueueName=constants.QUEUE_NAME)
    print(f'SQS queue "{constants.QUEUE_NAME}" created successfully')

    queue = sqs_resource.get_queue_by_name(QueueName=constants.QUEUE_NAME)
    sqs_client.set_queue_attributes(QueueUrl=queue.url, Attributes={'Policy': json.dumps(iam.sqs_policy.get())})
    print(f'SQS queue "{constants.QUEUE_NAME}" policy set successfully')
  except ClientError as e:
    print(e)

def create_bucket():
  print(f'\nCreating S3 bucket: {constants.BUCKET_NAME}')
  try:
    if constants.REGION is None:
      s3_client = boto3.client('s3')
      s3_client.create_bucket(Bucket=constants.BUCKET_NAME)
    else:
      s3_client = boto3.client('s3', region_name=constants.REGION)
      location_configuration = {
        'LocationConstraint': constants.REGION
      }
      s3_client.create_bucket(
        Bucket=constants.BUCKET_NAME,
        CreateBucketConfiguration=location_configuration
      )
    print(f'Bucket "{constants.BUCKET_NAME}" created successfully')
  except ClientError as e:
    print(e)

  s3_resource = boto3.resource('s3')
  try:
    bucket_notification = s3_resource.BucketNotification(constants.BUCKET_NAME)
    queue_configuration = {
      'QueueConfigurations': [
        {
          'Id': 'send-sqs-message-1703130',
          'QueueArn': f'arn:aws:sqs:{constants.REGION}:{constants.ACCOUNT_ID}:{constants.QUEUE_NAME}',
          'Events': [
            's3:ObjectCreated:Put'
          ]
        }
      ]
    }
    bucket_notification.put(NotificationConfiguration=queue_configuration)
    print(f'Bucket "{constants.BUCKET_NAME}" event notification set successfully')
  except ClientError as e:
    print(e)

def create_stack():
  print(f'\nCreating CloudFormation stack: {constants.STACK_NAME}')
  cf_client = boto3.client('cloudformation')
  try:
    with open('./cloudformation.json', 'rb') as f:
      template = f.read().decode()
      cf_client.create_stack(
        StackName=constants.STACK_NAME,
        TemplateBody=template,
      )
      print(f'Stack "{constants.STACK_NAME}" created successfully')
  except ClientError as e:
    print(e)

def create_lambda_iam():
  print(f'\nCreating IAM role: {constants.LAMBDA_ROLE_NAME}')
  iam_client = boto3.client('iam')
  role_service = {
    'Version': '2012-10-17',
    'Statement': [
      {
        'Effect': 'Allow',
        'Principal': {
          'Service': 'lambda.amazonaws.com'
        },
        'Action': 'sts:AssumeRole'
      }
    ]
  }

  try:
    role_response = iam_client.create_role(
      RoleName=constants.LAMBDA_ROLE_NAME,
      AssumeRolePolicyDocument=json.dumps(role_service),
      Description='Gives lambda functions permission to run specific services',
    )
    print(f'IAM role "{constants.LAMBDA_ROLE_NAME}" created successfully')
  except ClientError as e:
    print(e)

  try:
    policy_response = iam_client.create_policy(
      PolicyName=constants.LAMBDA_POLICY_NAME,
      PolicyDocument=json.dumps(iam.lambda_policy.get())
    )
    print(f'IAM policy "{constants.LAMBDA_POLICY_NAME}" created successfully')
  except ClientError as e:
    print(e)

  try:
    iam_client.attach_role_policy(
      PolicyArn=f'arn:aws:iam::{constants.ACCOUNT_ID}:policy/{constants.LAMBDA_POLICY_NAME}',
      RoleName=constants.LAMBDA_ROLE_NAME,
    )
    print(f'IAM policy "{constants.LAMBDA_POLICY_NAME}" successfully attached to the IAM role "{constants.LAMBDA_ROLE_NAME}"')
  except ClientError as e:
    print(e)

def create_lambda(update=False):
  lambda_client = boto3.client('lambda')
  zip_lambda_function()
  try:
    with open(constants.LAMBDA_ZIP, 'rb') as zipfile:
      if update:
        print(f'\nUpdating Lambda function: {constants.LAMBDA_NAME}')
        lambda_client.update_function_code(
          FunctionName=constants.LAMBDA_NAME,
          ZipFile=zipfile.read(),
          Publish=False
        )
        print(f'Lambda function "{constants.LAMBDA_NAME}" updated successfully')
      else:
        print(f'\nCreating Lambda function: {constants.LAMBDA_NAME}')
        lambda_client.create_function(
          FunctionName=constants.LAMBDA_NAME,
          Runtime='python3.8',
          Role=f'arn:aws:iam::{constants.ACCOUNT_ID}:role/{constants.LAMBDA_ROLE_NAME}',
          Handler='analyze_sentiment.handler',
          Code={
            'ZipFile': zipfile.read()
          },
          Description='Lambda function to analyze sentiment from an audio file stored in an S3 bucket',
          Timeout=1,
          Publish=False,
          PackageType='Zip'
        )
        print(f'Lambda function "{constants.LAMBDA_NAME}" created successfully')

        lambda_client.create_event_source_mapping(
          EventSourceArn=f'arn:aws:sqs:{constants.REGION}:{constants.ACCOUNT_ID}:{constants.QUEUE_NAME}',
          FunctionName=constants.LAMBDA_NAME,
          Enabled=True,
          BatchSize=1
        )
        print(f'Lambda function "{constants.LAMBDA_NAME}" trigger successfully added for SQS queue {constants.QUEUE_NAME}')
  except ClientError as e:
    print(e)
  # Remove the source zip file
  os.remove(constants.LAMBDA_ZIP)

def create_eventbridge_rule():
  print(f'\nCreating EventBridge rule: {constants.TRANSCRIPTION_EVENTBRIDGE_RULE}')
  lambda_client = boto3.client('lambda')
  eb_client = boto3.client('events')
  try:
    eb_client.put_rule(
      Name=constants.TRANSCRIPTION_EVENTBRIDGE_RULE,
      EventPattern=json.dumps({
        'source': [
          'aws.transcribe'
        ],
        'detail-type': [
          'Transcribe Job State Change'
        ],
        'detail': {
          'TranscriptionJobStatus': [
            'COMPLETED'
          ]
        }
      }),
      State='ENABLED',
      Description='Event that runs a lambda function when a transcription job finishes'
    )
    print(f'EventBridge rule "{constants.TRANSCRIPTION_EVENTBRIDGE_RULE}" created successfully')

    eb_client.put_targets(
      Rule=constants.TRANSCRIPTION_EVENTBRIDGE_RULE,
      Targets=[{
        'Id': constants.LAMBDA_NAME,
        'Arn': f'arn:aws:lambda:{constants.REGION}:{constants.ACCOUNT_ID}:function:{constants.LAMBDA_NAME}'
      }]
    )
    print(f'Target "{constants.LAMBDA_NAME}" added successfully to EventBridge rule "{constants.TRANSCRIPTION_EVENTBRIDGE_RULE}"')
  except ClientError as e:
    print(e)

  try:
    lambda_client.add_permission(
      FunctionName=constants.LAMBDA_NAME,
      StatementId='eventbridge-permission',
      Action='lambda:InvokeFunction',
      Principal='events.amazonaws.com',
      SourceArn=f'arn:aws:events:{constants.REGION}:{constants.ACCOUNT_ID}:rule/{constants.TRANSCRIPTION_EVENTBRIDGE_RULE}'
    )
    print(f'Permission for EventBridge rule "{constants.TRANSCRIPTION_EVENTBRIDGE_RULE}" to invoke Lambda function {constants.LAMBDA_NAME} added successfully')
  except ClientError as e:
    print(e)