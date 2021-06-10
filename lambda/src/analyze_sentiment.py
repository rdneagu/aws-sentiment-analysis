import json, boto3, urllib.request
from botocore.exceptions import ClientError

import comprehend, transcribe, sqs

dynamodb = boto3.client('dynamodb')
sns = boto3.client('sns')

def handler(event, context):
  res = {
    'statusCode': 200,
    'body': 'Lambda execution finished'
  }

  if transcribe.is_transcription_event(event):
    job_name = event['detail']['TranscriptionJobName']
    sentiment = comprehend.detect_sentiment(job_name)
    transcribe.delete_transcription(job_name)
    
    tmp = job_name.split('-')
    file_name = '-'.join(tmp[:-6])
    
    print(f'Sentiment detected ({sentiment}) for "{file_name}"')

    try:
      if "negative" in sentiment.lower():
        print('Sentiment is negative, sending SMS')
        sns.publish(
          PhoneNumber='ZZ-ZZZZZZZZZZZZ',
          Message=f'The audio file {file_name} returned a NEGATIVE sentiment'
        )
    except ClientError as e:
      print(f'Failed to publish SMS message: {job_name}')
      print(e)
        
    dynamodb.put_item(TableName='cw-ddb-1703130',
      Item={
        'AudioFilename': {
          'S': file_name
        },
        'Sentiment': {
          'S': sentiment
        },
      }
    )
  else:
    for record in event['Records']:
      body = json.loads(record['body'])
      
      if not sqs.is_sqs_queue(body):
        break
      
      for file in body['Records']:
        try:
          file_bucket = file['s3']['bucket']['name']
          file_name = file['s3']['object']['key']
          file_url = f'https://s3.amazonaws.com/{file_bucket}/{file_name}'
          job_name = f'{file_name}-{record["messageId"]}-1703130'
          transcribe.start_transcription(job_name, file_url)
          print(f'Transcription {job_name} started for "{file_name}"')
        except ClientError as e:
          print(e)

  return res
