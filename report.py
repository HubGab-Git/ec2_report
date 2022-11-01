from boto3 import client
from csv import writer
from re import match,findall
from datetime import datetime
from dateutil import relativedelta

### provide CPUUtilization for instanceID
def getCPUUtilization(instanceID):
    metrics = cloudWatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[
                {
                'Name': 'InstanceId',
                'Value': instanceID
                },
            ],
            StartTime=datetime.now() - relativedelta.relativedelta(months=6),
            EndTime=datetime.now(),
            Period= 60*60*24*30*6, # 6 months
            Statistics=[
                'Minimum','Maximum','Average'
            ],
            Unit='Percent'
        )
    minimum = None
    maximum = None
    averange = None

    for item in metrics["Datapoints"]:

        if minimum == None:
            minimum=item["Minimum"]
        elif minimum > item["Minimum"]:
            minimum=item["Minimum"]

        if maximum == None:
            maximum = item["Maximum"]
        elif maximum < item["Maximum"]:
            maximum = item["Maximum"]

        if averange == None:
            averange = item["Average"]
        else:
            averange = (averange + item["Average"])/2


    return {"minimum":minimum, "maximum":maximum, "averange":averange}


conn=client('ec2',region_name='us-east-1')
response = conn.describe_instances(MaxResults=300,)

cloudWatch = client('cloudwatch',region_name='us-east-1')

data = []
for reservation in response["Reservations"]:
   for instance in reservation["Instances"]:
        stopReason = "-"
        stopTime = '-'
        name = ''
        if instance["State"]["Name"] == "stopped":
            stopReason = instance['StateTransitionReason'].split('(')[0]
            if match('.*\((.*)\)', instance['StateTransitionReason']):
                stopTime = findall('.*\((.*)\)', instance['StateTransitionReason'])[0]

            cpu = {"minimum" : None, "maximum" : None, "averange" : None}
        else:
            cpu = getCPUUtilization(instance["InstanceId"])

        for tag in instance["Tags"]:
            if tag["Key"] == "Name":
                name=tag["Value"]
        
        cpu = getCPUUtilization(instance["InstanceId"])
        
        ### generate matrix table for each instance
        data.append([
            instance["InstanceId"], 
            name,
            instance["State"]["Name"], 
            instance["LaunchTime"],
            stopTime,
            stopReason,
            cpu["minimum"],
            cpu["maximum"],
            cpu['averange']
        ])

### Header for CSV file
header = [
    'InstanceID', 
    'InstanceName', 
    'State', 
    'LaunchTime', 
    'StoppedTime', 
    'Reason', 
    'MinCPUUtilization',
    'MaxCPUUtilization',
    'AvgCPUUtilization',
    ]

### Save CSV Report to report.csv
with open('report.csv', 'w', encoding='UTF8', newline='') as f:
    writer = writer(f,delimiter=";")
    writer.writerow(header)
    writer.writerows(data)