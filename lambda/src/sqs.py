def is_sqs_queue(body):
  return ('Records' in body)