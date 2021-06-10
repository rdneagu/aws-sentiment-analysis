import os, sys, threading
import boto3
from time import sleep

import constants

class ProgressPercentage(object):
    def __init__(self, filename):
      self._filename = filename
      self._size = float(os.path.getsize(filename))
      self._seen_so_far = 0
      self._lock = threading.Lock()

    def __call__(self, bytes_amount):
      with self._lock:
        self._seen_so_far += bytes_amount
        percentage = (self._seen_so_far / self._size) * 100
        sys.stdout.write(
          "\r%s  %s / %s  (%.2f%%)\n" % (
            self._filename, self._seen_so_far, self._size,
            percentage))
        sys.stdout.flush()

def upload_audio():
  s3 = boto3.client("s3")

  data_dir = 'data'
  for audio in os.listdir(data_dir):
    audio_path = os.path.join(data_dir, audio)
    print(f'Uploading the file {audio_path} to S3 bucket "{constants.BUCKET_NAME}"')
    s3.upload_file(audio_path, constants.BUCKET_NAME, audio, Callback=ProgressPercentage(audio_path))
    print(f'File {audio_path} successfully uploaded to S3 bucket "{constants.BUCKET_NAME}"')
    sleep(30)

upload_audio()