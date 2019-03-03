#!/usr/bin/python

###### Script will be used to spin up EC2 instances. In this example, I will be 
###### using AWS Free Tier account for these examples.


import click
import boto3
import configparser
import os
import logging
import sys
import json
import paramiko
import time
import coloredlogs

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)
coloredlogs.install(level='INFO', logger=log)

@click.group()
def main():
    """ This is a simple EC2 Command line tool"""
    config = configparser.RawConfigParser()
    config_path = os.getcwd() + '/config.txt'
    config.read(config_path)
    log.info("Reading from config file" + config_path)
    details_dict = dict(config.items('builder'))

    global access_key 
    access_key=config.get('builder','aws_access_key_id')
    global secret_key
    secret_key=config.get('builder','aws_secret_access_key')
    global region
    region=config.get('builder', 'region')
    pass
     
@click.command()
@click.option('--ami', help='What AWS AMI are you using?')
@click.option('--instancetype', help='AWS EC2 instance type')
@click.option('--vpc', help='VPC Id')
@click.option('--isweb',default=True,type=bool,help='Is this a web server')
@click.option('--subnet',help="Subnet ID")
@click.option('--key',help="Specify Key Name")
@click.pass_context
def build(ctx,ami,instancetype,vpc,isweb,subnet,key):
    """ Will build out the EC2 instance - Webserver for now. Many more to come! """
    log.info("Building EC2...")
    log.info("Collecting Information....")
    log.info("AMI: " + ami)
    log.info("Instance Type: " + instancetype)
    log.info("VPC Name: " + vpc)
    log.info("Is this a web server: " + str(isweb))        

    if isweb:
        log.info("Spinning up Web Server")
        try:
            ec2 = connection() 
            if ec2:
                log.info("AWS Session Created") 
                log.info("Gathering VPC ID...")
                sec_group = ec2.create_security_group(GroupName='webserver', Description='webserver', VpcId=vpc)
                log.info("Created Web SG...") 
                rule1 = sec_group.authorize_ingress( 
                     IpProtocol='tcp',
                     FromPort=80,
                     ToPort= 80,
                     CidrIp='0.0.0.0/0')
                rule2 = sec_group.authorize_ingress(
                     IpProtocol='tcp',
                     FromPort=22,
                     ToPort=22,
                     CidrIp='0.0.0.0/0')
                instances = ec2.create_instances(
                ImageId=ami, InstanceType=instancetype, MaxCount=1, MinCount=1, KeyName=key,
                NetworkInterfaces=[{'SubnetId': subnet, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group.group_id]}])
                instances[0].wait_until_running()
                log.info(instances[0].id)
                instances[0].load()
                instance_dns = instances[0].public_dns_name
                log.info(instance_dns)
                configure_web(instance_dns,key)
        except Exception as err:
            log.error(err)
	    sys.exit()
        if not isweb:
            log.error("Not a web server!! Goodbye! Will add more options later")
            sys.exit()


def configure_web(host,key):
    ssh_user = "ec2-user"
    log.info("Attempting to connect as " + ssh_user)
    try:
        log.info("Waiting for 60 seconds for EC2 instance to finish setting up..")
        time.sleep(60)        
        ssh = paramiko.SSHClient()
        key = paramiko.RSAKey.from_private_key_file(os.getcwd() +'/' +  key + '.pem')
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        connection = ssh.connect(hostname=host, username=ssh_user, pkey=key)
        log.info("Attempting Connection on host: " + host)
        log.info("Connection Successful...")
        try:
            apache_install='sudo yum install httpd -y'
            ssh_stdin, ssh_stdout, ssh_stderr=ssh.exec_command(apache_install)
            log.info(ssh_stdout)
            log.info("Apache install is Complete!!")
            time.sleep(5)
            apache_turnon(host,ssh_user,key)
        except Exception as brr:
            log.error(brr)
            sys.exit()
    except Exception as err:
        log.error(err)
        sys.exit()

@main.command()
@click.option('--instanceid',help='AWS Instance Id')
@click.option('--sgid',required=False,help='Coming Soon... For now, this is Optional')
@click.pass_context
def destroy(ctx,instanceid,sgid):
   """ Destroy EC2 Instance """
   log.info("Terminating Instance...")
   try:
       ec2 = connection()
       instance = ec2.Instance(instanceid)
       instance.terminate()
       log.info("Instance ID: " + instanceid + " is destroyed.")
   except Exception as err:
       log.error(err)
       sys.exit() 

def apache_turnon(host,ssh_user,key):
    ## Need to see why I can't str concat on key variable. I am passing ssh_key as the variable - when I tried printing it out, it seemed to print characters out. I will fix this at a later date. 
    ssh = paramiko.SSHClient()
    key = paramiko.RSAKey.from_private_key_file(os.getcwd() + '/test2.pem')
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    connection = ssh.connect(hostname=host, username=ssh_user, pkey=ssh_key)
    service_on='sudo service httpd start'
    ssh_stdn, ssh_stdout, ssh_stderr=ssh.exec_command(service_on)
    log.info("Try accessing the website: http://" + host + ":80")
    log.info('All set now!! If you need to SSH into the server, make sure to download your PEM key and place it in the project directory')

def connection():
    connection = boto3.resource('ec2', aws_access_key_id=access_key,  aws_secret_access_key=secret_key, region_name=region)
    return connection
   
main.add_command(build)
main.add_command(destroy)

if __name__ == "__main__": main()
