from obscreator.obs import Obs
from drivers.driver import ObsDriver
from logger import logger
import boto3
from botocore.exceptions import ClientError
import conf
import json
import os
from datetime import datetime

logger.info("Starting SIBot..")

sqs = boto3.resource('sqs', region_name=conf.SQS_REGION_NAME,
                     aws_access_key_id=conf.SQS_ACCESS_KEY_ID,
                     aws_secret_access_key=conf.SQS_SECRET_ACCESS_KEY)

try:
    request_queue = sqs.get_queue_by_name(QueueName=conf.SQS_REQUEST_QUEUE_NAME)
    request_queue.attributes['ReceiveMessageWaitTimeSeconds'] = '20'

    logger.info(f"Subscribed to {request_queue.url}")
except ClientError as e:
    if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
        logger.error(f"Unable to subscribe to Non Existent queue: {conf.SQS_REQUEST_QUEUE_NAME}")
    raise e

try:
    success_queue = sqs.get_queue_by_name(QueueName=conf.SQS_RESPONSE_QUEUE_NAME)

except ClientError as e:
    if e.response['Error']['Code'] == 'AWS.SimpleQueueService.NonExistentQueue':
        success_queue = sqs.create_queue(QueueName=conf.SQS_RESPONSE_QUEUE_NAME)
        logger.info(f"{conf.SQS_RESPONSE_QUEUE_NAME} created.")
    else:
        raise e

success_queue.attributes['DelaySeconds'] = '5'
logger.info('SIBot started')

logger.info('Polling for message...')
while True:
    logger.info('.')
    messages = request_queue.receive_messages(MaxNumberOfMessages=1)  # AttributeNames=['All']
    for message in messages:
        logger.info(message.body)
        msg = json.loads(message.body)

        # drop this message in folder and remove it from SQS
        file_name = f"{msg['recordId']}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
        with open(os.path.join(conf.REQUEST_DROPBOX, file_name), 'w') as f:
            json.dump(msg, f)

        message.delete()

        driver = ObsDriver()
        try:
            obs = Obs(driver)
            obs_id = obs.create_obs(msg)

            new_obs_message = {
                "status": 'success',
                "recordId": msg['recordId'],
                "obsId": obs_id
            }
            new_obs_attribute = {
                "Host": {
                    'StringValue': os.environ['COMPUTERNAME'],
                    'DataType': 'String'
                }
            }
            response = success_queue.send_message(MessageBody=json.dumps(new_obs_message, indent=None),
                                                  MessageAttributes=new_obs_attribute)
            logger.info(
                f"Success message (id:{response.get('MessageId')}) delivered {response.get('MD5OfMessageBody')}")

        except Exception:
            import sys
            import traceback

            traceback.print_exc()
        finally:
            driver.close()
