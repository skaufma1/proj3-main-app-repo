from flask import Flask, request, redirect, url_for, render_template
import boto3

ec2 = boto3.client("ec2")

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    # Retrieve all instances
    response = ec2.describe_instances()

    # Sort instances by state
    sorted_instances = sorted(response['Reservations'], key=lambda k: k['Instances'][0]['State']['Name'])

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

    return render_template('home.html', instances=response['Reservations'])

@app.route('/ec2_instances_popup', methods=['GET', 'POST'])
def show_ec2_instances():
    # Retrieve all instances
    response = ec2.describe_instances()
    # Sort instances by state
    sorted_instances = sorted(response['Reservations'], key=lambda k: k['Instances'][0]['State']['Name'])

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
    return render_template('ec2_instances_popup.html', instances=sorted_instances)

if __name__ == "__main__":
    app.run(debug=True)