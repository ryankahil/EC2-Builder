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

log = logging.getLogger(__name__)
out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
out_hdlr.setLevel(logging.INFO)
log.addHandler(out_hdlr)
log.setLevel(logging.INFO)

@click.group()
def main():
    """ This is a simple EC2 Command line tool"""
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
    """ Will build out the EC2 instance """
    log.info("Building EC2...")
    log.info("Collecting Information....")
    log.info("AMI: " + ami)
    log.info("Instance Type: " + instancetype)
    log.info("VPC Name: " + vpc)
    log.info("Is this a web server: " + str(isweb))        

    if isweb:
        log.info("Spinning up Web Server")
        log.info("Reading from config file")
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
                configure_web()
        except Exception as err:
            log.error(err)
	    sys.exit()
        if not isweb:
            log.error("Not a web server!! Goodbye! Will add more options later")
            sys.exit()


def configure_web():
    log.info("Will be configuring Apache now..")

@main.command()
@click.option('--instanceid',help='AWS Instance Id')
@click.pass_context
def destroy(ctx,instanceid):
   """ Destroy EC2 Instance and Security group """
   log.info("Terminating Instance...")
   try:
       ec2 = connection()
       instance = ec2.Instance(instanceid)
       instance.terminate()
       log.info("Instance ID: " + instanceid + " is destroyed.")
   except Exception as err:
       log.error(err)
       sys.exit()

def connection():
    config = configparser.RawConfigParser()
    config_path = os.getcwd() + '/config.txt'
    config.read(config_path)
    log.info("Reading from config file" + config_path)
    details_dict = dict(config.items('builder'))

    access_key = config.get('builder','aws_access_key_id')
    secret_key = config.get('builder','aws_secret_access_key')
    region = config.get('builder', 'region')

    connection = boto3.resource('ec2', aws_access_key_id=access_key,  aws_secret_access_key=secret_key, region_name=region)
    return connection
   
main.add_command(build)

if __name__ == "__main__": main()
