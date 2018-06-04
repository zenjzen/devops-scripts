"""This module determines what instances need etcd and tags them as such.
Designed to be used in 2 master 2 node k8s cluster in aws prior to running
kubespray. Designed to be run in jenkins using jenkins secrets."""

import os
import boto3

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
REGION_NAME = os.environ['REGION']

def main(access_key_id, secret_access_key, region):
    '''tag ec2 instances with etcd if the right parameters exist'''
    ec2 = boto3.client(
        'ec2',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region
    )

    k8s_masters = ec2.describe_tags(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': ['DEV-Kubernetes-Master']
            }
        ]
    )

    k8s_masters_ids = []

    for key in k8s_masters['Tags']:
        k8s_masters_ids.append(key['ResourceId'])

    tag_masters(ec2, k8s_masters_ids)

    k8s_nodes = ec2.describe_tags(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': ['DEV-Kubernetes-Node']
            }
        ]
    )

    k8s_nodes_ids = []

    for key in k8s_nodes['Tags']:
        k8s_nodes_ids.append(key['ResourceId'])

    tag_nodes(ec2, k8s_nodes_ids)

    print "Tagging complete"

def tag_masters(ec2, k8s_masters_ids):
    '''check if masters are tagged with etcd and then tag if necessary'''
    k8s_masters = ec2.describe_tags(
        Filters=[
            {
                'Name': 'resource-id',
                'Values': k8s_masters_ids
            },
        ]
    )

    for key in k8s_masters['Tags']:
        if key['Value'] != 'kube-master, etcd':
            if key['Key'] == 'kubespray-role':
                tag = ec2.create_tags(
                    Resources=[
                        key['ResourceId'],
                    ],
                    Tags=[
                        {
                            'Key': 'kubespray-role',
                            'Value': 'kube-master, etcd'
                        }
                    ]
                )

                print tag
                print(key['ResourceId'], 'tagged with "kubespray-role": "kube-master, etcd"')
        else:
            print(key['ResourceId'], 'does not need to be tagged')

def tag_nodes(ec2, k8s_nodes_ids):
    '''check if nodes are tagged with etcd and then tag if necessary'''
    k8s_nodes = ec2.describe_tags(
        Filters=[
            {
                'Name': 'resource-id',
                'Values': k8s_nodes_ids
            },
        ]
    )

    k8s_tagged_nodes = []

    for key in k8s_nodes['Tags']:
        if key['Value'] == 'kube-node, etcd':
            k8s_tagged_nodes.append(key['ResourceId'])

    if not k8s_tagged_nodes:
        tag = ec2.create_tags(
            Resources=[
                k8s_nodes_ids[0],
            ],
            Tags=[
                {
                    'Key': 'kubespray-role',
                    'Value': 'kube-node, etcd'
                }
            ]
        )

        print tag
        print(k8s_nodes_ids[0], 'tagged with "kubespray-role": "kube-node, etcd"')
    else:
        print(k8s_nodes_ids, 'do not need to be tagged')


main(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION_NAME)
