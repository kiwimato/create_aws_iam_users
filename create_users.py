#!/usr/bin/env python3
# by kiwimato

import csv
import boto3
import random
import string
import os
from jinja2 import Environment, FileSystemLoader
from password_strength import PasswordPolicy

# Default groups for all users:
users_filename = "aws_users.csv"
groups = ['group1', 'group2']
aws_account_id = "XXXXXXXXXXXX"

session = boto3.Session(profile_name='default')
iam = session.client('iam')
iam_resource = session.resource('iam')


def gen_password(N):
    return ''.join(
        random.SystemRandom().choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(N))


# In case you have a AWS password policy this makes sure to generate a password that matches it.
def random_password(N):
    policy = PasswordPolicy.from_names(
        length=N,  # min length: 14
        uppercase=1,  # need min. 1 uppercase letters
        nonletterslc=1,  # need min. 1 lowercase letters
        numbers=1,  # need min. 1 digits
        special=1,  # need min. 1 special characters
        nonletters=1,  # need min. 1 non-letter characters (digits, specials, anything)
    )

    while True:
        password = gen_password(N)
        if not policy.test(password):
            return password


def create_password(iam, username):
    password = random_password(42)
    try:
        response = iam.create_login_profile(
            UserName=username,
            Password=password,
            PasswordResetRequired=True
        )
    except:
        print(f" => ERROR creating password for user {username} Password: {password}")

    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        print(f"\nAWS Username: {username} Password: {password}")
    return password


def user_exists(iam, user):
    try:
        iam.get_user(UserName=user)
    except iam.exceptions.NoSuchEntityException:
        return False
    return True


def create_user(iam, username, name, email):
    response = iam.create_user(
        UserName=username,
        Tags=[
            {
                'Key': 'name',
                'Value': name
            },
            {
                'Key': 'email',
                'Value': email
            },
            {
                'Key': 'create_automated',
                'Value': 'true'
            },
        ]
    )
    if response['User']['UserName'] == username:
        return True
    else:
        return False


def add_user_2_group(iam, username, groups):
    iam_user = iam.User(username)
    for group in groups:
        response = iam_user.add_group(GroupName=group)
        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
            print(f" => OK, assigned to group {group}", end='')
        else:
            print(f" => ERROR assigning to group {group}", end='')
    print("")


def compose_email_link(aws_account_id, username):
    return f"<a href='mailto:?subject=Welcome%20to%20Amazon%20Web%20Services&amp;body=Hello,%0A%0AYou%20have%20been%20given%20access%20to%20the%20AWS%20Management%20Console%20for%20the%20Amazon%20Web%20Services%20account%20with%20the%20ID%20ending%20in%20{aws_account_id[-3:]}.%20You%20can%20get%20started%20by%20using%20the%20sign-in%20information%20provided%20below.%0A%0A-------------------------------------------------%0A%0ASign-in%20URL:%20https://{aws_account_id}.signin.aws.amazon.com/console%0AUser%20name:{username}%20%0A%0AYour%20initial%20sign-in%20password%20will%20be%20provided%20to%20you%20by%20your%20AWS%20account%20administrator,%20separately%20from%20this%20email.%20When%20you%20sign%20in%20for%20the%20first%20time,%20you%20must%20change%20your%20password.%0A%0A-------------------------------------------------%0A%0AStay%20connected%20with%20AWS%20by%20creating%20a%20profile:%20https://pages.awscloud.com/IAM-communication-preferences.html%0A%0ASincerely,%0AYour%20AWS%20Account%20Administrator'> Send e-mail </a>"


with open(users_filename, newline='') as csvfile:
    user_file = csv.reader(csvfile, delimiter=',', quotechar='"')
    table = []
    for user in user_file:
        name = user[0].split(',')
        full_name = f"{name[1]} {name[0]}"
        email = user[1]
        username = user[1].split('@')[0]
        print(f"Searching if username: {username} already exists for Name:{full_name} e-mail:{email} ")

        if not user_exists(iam, username):
            print("\t Trying to create user", end='')
            if create_user(iam, username, full_name, email):
                print(f" => {username} created successfully!", end='')
                add_user_2_group(iam_resource, username, groups)
                password = create_password(iam, username)
                email_link = compose_email_link(aws_account_id, username)
                table.append({'name': full_name, 'username': username, 'password': password, 'link': email_link})
            else:
                print(f" => ERROR on creating user {username}!")
        else:
            print(f"\t ERROR: username: {username} already exists")

env = Environment(loader=FileSystemLoader(os.chdir(os.path.dirname(__file__))))
template = env.get_template("jinja2_template.html")  # the template file name
htmlcode = template.render(table=table)

with open('result.html', 'w+') as resultfile:
    resultfile.write(htmlcode)
