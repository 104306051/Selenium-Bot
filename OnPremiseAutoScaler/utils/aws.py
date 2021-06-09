import os
import boto3


def aws_client(resource_name):
    session = boto3.Session()
    return session.client(
        resource_name,
        aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        region_name=os.environ.get('AWS_REGION', 'us-east-2')
    )


def create_metric_data_queries(queue_name):
    return [
        {
            "Id": "e1",
            "Expression": "IF(m2==0, m1, m1/m2)",
            "Label": "MessageProcessingRatio"
        },
        {
            "Id": "m1",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/SQS",
                    "MetricName": "NumberOfMessagesSent",
                    "Dimensions": [
                        {
                            "Name": "QueueName",
                            "Value": queue_name
                        }
                    ]
                },
                "Period": 60,
                "Stat": "Sum",
                "Unit": "Count"
            },
            "ReturnData": True
        },
        {
            "Id": "m2",
            "MetricStat": {
                "Metric": {
                    "Namespace": "AWS/SQS",
                    "MetricName": "NumberOfMessagesReceived",
                    "Dimensions": [
                        {
                            "Name": "QueueName",
                            "Value": queue_name
                        }
                    ]
                },
                "Period": 60,
                "Stat": "Sum",
                "Unit": "Count"
            },
            "ReturnData": True
        }
    ]