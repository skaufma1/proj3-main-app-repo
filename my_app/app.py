import os
from flask import Flask, request, redirect, url_for, render_template
import jenkins
import boto3

os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'

ec2 = boto3.client("ec2")

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    # Retrieve all instances
    response = ec2.describe_instances()

    # Count instances in each state
    stopped_count = 0
    running_count = 0
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'stopped':
                stopped_count += 1
            elif instance['State']['Name'] == 'running':
                running_count += 1

    return render_template('home.html', instances=response['Reservations'], stopped_count=stopped_count, running_count=running_count)

@app.route('/ec2_instances_popup', methods=['GET', 'POST'])
def show_ec2_instances():
    # Retrieve all instances
    response = ec2.describe_instances()
    # Sort instances by state
    sorted_instances = sorted(response['Reservations'], key=lambda k: k['Instances'][0]['State']['Name'])

    # Count instances in each state
    stopped_count = 0
    running_count = 0
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            if instance['State']['Name'] == 'stopped':
                stopped_count += 1
            elif instance['State']['Name'] == 'running':
                running_count += 1

    # Handle form submission
    if request.method == 'POST':
        instance_ids = request.form.getlist('instance_ids')
        action = request.form['action']
        if instance_ids and action:
            if action == 'stop':
                ec2.stop_instances(InstanceIds=instance_ids)
            elif action == 'start':
                ec2.start_instances(InstanceIds=instance_ids)
            elif action == 'terminate':
                ec2.terminate_instances(InstanceIds=instance_ids)
    else:
        return render_template('ec2_instances_popup.html', instances=sorted_instances, stopped_count=stopped_count, running_count=running_count)

    # Loop through the response to print the instance summary
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']
            instance_state = instance['State']['Name']
            instance_public_ip = instance.get('PublicIpAddress', 'None')
            instance_private_ip = instance.get('PrivateIpAddress', 'None')
            instance_name = ''
            for tag in instance['Tags']:
                if tag['Key'] == 'Name':
                    instance_name = tag['Value']
                    break
            print(f"Instance: {instance_id} ({instance_name}), Type: {instance_type}, State: {instance_state}, Public IP: {instance_public_ip}, Private IP: {instance_private_ip}")

    # Pass data to template
    return render_template('ec2_instances_popup.html', instances=sorted_instances, stopped_count=stopped_count, running_count=running_count)

@app.route('/ec2_create_popup', methods=['GET', 'POST'])
def cre_ec2_instance():

    # Handle form submission
    if request.method == 'POST':
        new_instance_name = request.form.get("name")

        ec2 = boto3.resource("ec2")
        instance_type = "t2.micro"
        key_pair_name = "proj1-flask-master"
        image_id = "ami-09cd747c78a9add63"
        security_group_id = "sg-0be101c0f47493d2e"

        instance = ec2.create_instances(
            ImageId=image_id,
            InstanceType=instance_type,
            KeyName=key_pair_name,
            SecurityGroupIds=[security_group_id],
            MinCount=1,
            MaxCount=1,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                        'Key': 'Name',
                        'Value': new_instance_name
                        },
                    ]
                },
            ]
        )[0]

    return render_template("ec2_create_popup.html")

@app.route('/deploy_to_prod_popup', methods=['GET', 'POST'])
def deploy_to_prod():

    # Handle form submission
    if request.method == 'POST':
        server = jenkins.Jenkins('http://44.207.81.36:8080/', username='skaufma', password='Aa123456')

        job_name = 'Proj3_TestFlask_Deploy2Prod'
        selected_server = request.form['server']
        parameters = {'ServerToDeployTo': selected_server}
        server.build_job(job_name, parameters=parameters)

    return render_template("deploy_to_prod.html")

@app.route('/from_test_to_prod_cycle_popup', methods=['GET', 'POST'])
def from_test_to_prod_cycle_popup():

    # Handle form submission
    if request.method == 'POST':
        server = jenkins.Jenkins('http://44.207.81.36:8080/', username='skaufma', password='Aa123456')

        job_name = 'Proj3_Flask_Main'
        server.build_job(job_name)

    return render_template("from_test_to_prod_cycle_popup.html")

@app.route('/new_iam_user_cre_popup', methods=['GET', 'POST'])
def new_iam_user_cre_popup():
    # Handle form submission
    if request.method == 'POST':
        iam = boto3.client("iam")
        new_username = request.form['username']

        try:
            # Create the IAM user
            response = iam.create_user(UserName = new_username)

            message = f'IAM user created successfully: {response["User"]["UserName"]}'

            # Assign a temporary password
            response = iam.create_login_profile(
                UserName = new_username,
                Password = 'Password@1234',
                PasswordResetRequired = True
            )

            response = iam.add_user_to_group(
                GroupName = "EC2-S3-FullAccess",
                UserName = new_username
            )

            return render_template("new_iam_user_cre_popup.html", message=message)

        except iam.exceptions.EntityAlreadyExistsException:
            message = f'ERROR: IAM user with the username "{new_username}" already exists.'

            return render_template("new_iam_user_cre_popup.html", message=message)

    else:
        return render_template("new_iam_user_cre_popup.html")

if __name__ == "__main__":
    app.run(debug=True)