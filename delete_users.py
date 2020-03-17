#!/usr/bin/env python3
import boto3

groups = ['group1', 'group2']

session = boto3.Session(profile_name='default')
iam = session.client('iam')

already_created_users = iam.list_users()

for user in already_created_users['Users']:
    tags = iam.list_user_tags(UserName=user['UserName'])
    username = user['UserName']

    for tag in tags['Tags']:
        if tag['Key'] == 'create_automated' and tag['Value'] == 'true':
            print(username)
            iam.delete_login_profile(UserName=username)
            for group in groups:
                iam.remove_user_from_group(GroupName=group, UserName=username)
            iam.delete_user(UserName=username)
