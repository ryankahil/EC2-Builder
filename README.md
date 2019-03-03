# EC2-Builder

This is a simple CLI program in Python 2.7 that will spin up an EC2 instance. This will spin up a web server for now. Future plans are to create multiple options (i.e load balancer, mysql server, etc.)


## Set up:

1. Clone the repository:

```
git clone git@github.com:ryankahil/EC2-Builder.git
```

2. In your AWS account, create a programmatic user in IAM and provide it EC2:FullAccess permissions. Download the CSV file.
3. You will need to create a config.txt in the project directory that will contain the access key and secret key generated in AWS. Should be in this format:
4. You will need to run the following command to download some of the dependencies for the code:

```
pip install -r requirements.txt
```

```
[builder]
aws_access_key_id = <access_key>
aws_secret_access_key = <secret_access_key>
vpc = <VPC_ID>
region = <region>
```


Then you should be ready to go!! 


## Main Menu

Here is the main menu. There are two commands: build and destroy

```
Usage: ec2-build.py [OPTIONS] COMMAND [ARGS]...

  This is a simple EC2 Command line tool

Options:
  --help  Show this message and exit.

Commands:
  build    Will build out the EC2 instance - Webserver for now.
  destroy  Destroy EC2 Instance
```

## Build
This will build out your EC2 instance with your basic Apache web server:

```
Usage: ec2-build.py build [OPTIONS]

  Will build out the EC2 instance - Webserver for now. Many more to come!

Options:
  --ami TEXT           What AWS AMI are you using?
  --instancetype TEXT  AWS EC2 instance type
  --vpc TEXT           VPC Id
  --isweb BOOLEAN      Is this a web server
  --subnet TEXT        Subnet ID
  --key TEXT           Specify Key Name
  --help               Show this message and exit.
```

Here is an example of how this is run:

```
python ec2-build.py build --ami ami-0c134a006c1eda4f6 --instancetype t2.micro --vpc vpc-e8269d92 --isweb True --key test2 --subnet subnet-1422021b
```

## Destroy
This will destroy the EC2 instance.

```
Usage: ec2-build.py destroy [OPTIONS]

  Destroy EC2 Instance

Options:
  --instanceid TEXT  AWS Instance Id
  --sgid TEXT        Coming Soon... For now, this is Optional
  --help             Show this message and exit.

```

Here is an example of how this is run:

```
python ec2-build.py destroy --instanceid 'i-061b4a8521f0581e4'
```
