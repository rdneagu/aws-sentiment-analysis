import json, boto3, urllib.request
from botocore.exceptions import ClientError

import transcribe

comprehend = boto3.client('comprehend')

def detect_sentiment(transcribe_job_name):
  try:
    transcribe_job = transcribe.get_transcription(transcribe_job_name)
    uri = transcribe_job['TranscriptionJob']['Transcript']['TranscriptFileUri']
    
    content = urllib.request.urlopen(uri).read().decode('UTF-8')
    
    data = json.loads(content)
    transcribed_text = data['results']['transcripts'][0]['transcript']
    
    sentiment = comprehend.detect_sentiment(
      Text=transcribed_text,
      LanguageCode='en'
    )['Sentiment']
    return sentiment
  except ClientError as e:
    print(f'Could not detect sentiment for: {job_name}')
    print(e)
    