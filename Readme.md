# Create AWS IAM users from CSV

This is a python script that will create AWS IAM users that are loaded from a CSV, and assign them to groups.
It's useful when you have to create let's say 100 AWS IAM users, and don't want to create them manually.
It will also output a result.html with the hidden password and a mailto: link for each one which can be sent to each one.


## Installation
```
python3 -m venv toolkit
source toolkit/bin/activate
pip install -r requirements.txt
```

## Configuration:
Simply populate aws_users.csv with the users. The AWS username will be the string before @ sign in the e-mail.
Also, in case you have AWS password policies make sure to tweak `create_users.py:26`

## Usage:
```
./create_users.py
```
This will create the result.html file which you can open in a browser so you can send e-mails to the users.
TODO: HTML escape passwords because some passwords that have `><` chars are rendered by the browser and you need to check the source if you want to see the full password. 

Sometimes you need to delete them, so there's the `delete_users.py` script for that.