# EC2-Builder

This is a simple CLI program in Python 2.7 that will spin up an EC2 instance. This will spin up a web server for now. Future plans are to create multiple options (i.e load balancer, mysql server, etc.)


## Set up:

1. Clone the repository
2. In your AWS account, create a programmatic user in IAM and provide it EC2:FullAccess permissions. Download the CSV file.
3. You will need to create a config.txt that will contain the access key and secret key generated in AWS. Should be in this format:

`[builder]
aws_access_key_id = <access_key>
aws_secret_access_key = <secret_access_key>
vpc = <VPC_ID>
region = <region>`

Then you should be ready to go!! 
