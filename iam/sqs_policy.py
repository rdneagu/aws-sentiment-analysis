import constants

def get():
  return {
    'Version': '2012-10-17',
    'Statement': [
      {
        'Effect': 'Allow',
        'Principal': {
          'Service': 's3.amazonaws.com'
        },
        'Action': 'sqs:SendMessage',
        'Resource': f'arn:aws:sqs:{constants.REGION}:{constants.ACCOUNT_ID}:{constants.QUEUE_NAME}',
        'Condition': {
          'ArnLike': {
            'aws:SourceArn': f'arn:aws:s3:::{constants.BUCKET_NAME}'
          }
        }
      }
    ]
  }
