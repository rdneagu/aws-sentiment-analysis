import constants

def get():
  return {
    'Version': '2012-10-17',
    'Statement': [
      {
        'Sid': 'sqsPermissions',
        'Effect': 'Allow',
        'Action': [
          'sqs:DeleteMessage',
          'sqs:ReceiveMessage',
          'sqs:GetQueueAttributes'
        ],
        'Resource': f'arn:aws:sqs:{constants.REGION}:{constants.ACCOUNT_ID}:{constants.QUEUE_NAME}'
      },
      {
        'Sid': 's3Permissions',
        'Effect': 'Allow',
        'Action': 's3:GetObject',
        'Resource': f'arn:aws:s3:::{constants.BUCKET_NAME}/*'
      },
      {
        'Sid': 'dynamodbPermissions',
        'Effect': 'Allow',
        'Action': 'dynamodb:PutItem',
        'Resource': f'arn:aws:dynamodb:{constants.REGION}:{constants.ACCOUNT_ID}:table/{constants.DDB_TABLE}'
      },
      {
        'Sid': 'snsPermissions',
        'Effect': 'Allow',
        'Action': 'sns:Publish',
        'Resource': '*'
      },
      {
        'Sid': 'transcribePermissions',
        'Effect': 'Allow',
        'Action': [
          'transcribe:GetTranscriptionJob',
          'transcribe:StartTranscriptionJob',
          'transcribe:DeleteTranscriptionJob'
        ],
        'Resource': '*'
      },
      {
        'Sid': 'cloudwatchPermissions',
        'Effect': 'Allow',
        'Action': [
          'logs:CreateLogStream',
          'logs:GetLogEvents',
          'logs:FilterLogEvents',
          'logs:CreateLogGroup',
          'logs:PutLogEvents'
        ],
        'Resource': '*'
      },
      {
        'Sid': 'comprehendPermissions',
        'Effect': 'Allow',
        'Action': 'comprehend:DetectSentiment',
        'Resource': '*'
      }
    ]
  }
