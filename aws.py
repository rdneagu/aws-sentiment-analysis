from time import sleep

from lib.create_resources import *
from lib.delete_resources import *

import constants

def delete_aws():
  delete_eventbridge_rule()
  sleep(1)
  delete_lambda_iam()
  sleep(1)
  delete_lambda()
  sleep(1)
  delete_sqs()
  sleep(1)
  delete_bucket()
  sleep(1)
  delete_stack()

def create_aws():
  create_stack()
  sleep(1)
  create_sqs()
  sleep(1)
  create_bucket()
  sleep(1)
  create_lambda_iam()
  sleep(10) # At least 10 seconds required to make sure the IAM role is fully created
  create_lambda(update=False)
  sleep(1)
  create_eventbridge_rule()

def update_lambda_code():
  create_lambda(update=True)

create_aws()
# delete_aws()
# update_lambda_code()