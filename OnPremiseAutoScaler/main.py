import os
import sys
from datetime import datetime, timedelta

from onpremiseautoscaler import OnPremiseAutoScaler
from utils.aws import aws_client, create_metric_data_queries
import logging

FORMAT = '%(asctime)s %(levelname)s: %(message)s'
logging.basicConfig(level=logging.INFO, filename='./logs/SibotAutoScalerLog.log', filemode='a', format=FORMAT)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
cloudwatch = aws_client(resource_name='cloudwatch')
now = datetime.now().replace(second=0, microsecond=0)
data = cloudwatch.get_metric_data(
    MetricDataQueries=create_metric_data_queries(os.environ.get("QUEUE_NAME", "sherlock-serverless-testing-obscreationrequest")),
    StartTime=now - timedelta(seconds=int(os.environ.get("METRIC_INTERVAL", 240))),
    EndTime=now,
    )

logging.debug(f'data: {data}')
message_processing_ratio = [metric_dict for metric_dict in data['MetricDataResults'] if metric_dict['Id'] == 'e1'][0]['Values'][0]
logging.info(f'Current Ratio: {message_processing_ratio}')
# ssm = aws_client(resource_name='ssm')
# access_key_param = ssm.get_parameter(Name=os.environ.get('SSM_AK_KEY_NAME'), WithDecryption=True)
# secret_key_param = ssm.get_parameter(Name=os.environ.get('SSM_SK_KEY_NAME'), WithDecryption=True)
# access_key = access_key_param['Parameter']['Value']
# secret_key = secret_key_param['Parameter']['Value']

auto_scaler = OnPremiseAutoScaler(image_name=os.environ.get('CONSUMER_IMAGE_NAME', 'sibot'),
                                  app_name=os.environ.get('CONSUMER_APP_NAME', 'sibot'),
                                  min_size=int(os.environ.get('CONSUMER_MIN_SIZE', 3)))
auto_scaler.scale(message_processing_ratio, os.environ['AWS_ACCESS_KEY_ID'], os.environ['AWS_SECRET_ACCESS_KEY'])
