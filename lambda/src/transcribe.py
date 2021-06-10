import json, boto3, urllib.request
from botocore.exceptions import ClientError

transcribe = boto3.client('transcribe')

def start_transcription(job_name, file_url):
  return transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    LanguageCode='en-US',
    MediaFormat='mp3',
    Media={
      'MediaFileUri': file_url
  })
        
def get_transcription(job_name):
  return transcribe.get_transcription_job(TranscriptionJobName=job_name)
    
def delete_transcription(job_name):
  try:
    transcribe.delete_transcription_job(TranscriptionJobName=job_name)
  except ClientError as e:
    print(f'Could not delete transcription job: {job_name}')
    print(e)
        
def is_transcription_event(event):
  return ('source' in event and 'aws.transcribe' in event['source'])