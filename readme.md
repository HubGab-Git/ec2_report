# EC2 Report

## Description

Python script for boto3 which generate csv file with averange data from last 6 months:

```md
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
```