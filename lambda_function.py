import boto3
from datetime import datetime, timedelta

ec2 = boto3.client('ec2')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    print("Lambda started")

    instances = ec2.describe_instances()
    print("Instances fetched")

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            print(f"Checking instance: {instance_id}")

            metrics = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.utcnow() - timedelta(minutes=10),
                EndTime=datetime.utcnow(),
                Period=300,
                Statistics=['Average']
            )

            print(f"Metrics: {metrics}")

            if metrics['Datapoints']:
                cpu = metrics['Datapoints'][0]['Average']
                print(f"{instance_id} CPU: {cpu}")

                if cpu < 5:
                    print(f"Stopping {instance_id}")
                    ec2.stop_instances(InstanceIds=[instance_id])
            else:
                print(f"No CPU data for {instance_id}")
