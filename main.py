import boto3
import time
from botocore.config import Config

config = Config(
    retries = dict(
        max_attempts = 10
    )
)

millis = int(round(time.time() * 1000))

delete = False
debug = True
log_group_prefix='/' # NEED TO CHANGE THESE

days = 90
# Create CloudWatchLogs client
cloudwatch_logs = boto3.client('logs', config=config)

log_groups=[]
# List log groups through the pagination interface
paginator = cloudwatch_logs.get_paginator('describe_log_groups')
for response in paginator.paginate(logGroupNamePrefix=log_group_prefix):
    for log_group in response['logGroups']:
        log_groups.append(log_group['logGroupName'])

if debug:
    print(log_groups)

old_log_groups=[]
empty_log_groups=[]
for log_group in log_groups:
    response = cloudwatch_logs.describe_log_streams(
        logGroupName=log_group, #logStreamNamePrefix='',
        orderBy='LastEventTime',
        descending=True,
        limit=1
    )
    # The time of the most recent log event in the log stream in CloudWatch Logs. This number is expressed as the number of milliseconds after Jan 1, 1970 00:00:00 UTC.
    if len(response['logStreams']) > 0:
        if debug:
            print("full response is:")
            print(response)
            print("Last event is:")
            print(response['logStreams'][0].get('lastEventTimestamp'))
            print("current millis is:")
            print(millis)
        if response['logStreams'][0].get('lastEventTimestamp'):
            if response['logStreams'][0]['lastEventTimestamp'] < millis - (days * 24 * 60 * 60 * 1000):
                old_log_groups.append(log_group)
        else:
            print(response['logStreams'][0]["arn"])
    else:
        empty_log_groups.append(log_group)

# delete log group
if delete:
    for log_group in old_log_groups:
        response = cloudwatch_logs.delete_log_group(logGroupName=log_group)
        print(response)
    for log_group in empty_log_groups:
        response = cloudwatch_logs.delete_log_group(logGroupName=log_group)
        print(response)
else:
    print("old log groups are:")
    print(old_log_groups)
    print("Number of log groups:")
    print(len(old_log_groups))
    print("empty log groups are:")
    print(empty_log_groups)
