# Report Getter

This creates an AWS lambda function that runs once per day and checks on a URL.  It emails you whatever the contents of the URL are.

# Setup

Edit the `secrets.tf_TEMPLATE` to reflect the desired email settings.  Run make to create the deployment code zip file.  Run `AWS_PROFILE="profile_name" terraform apply` to deploy the lambda and security settings.

# Usage

The lambda will run via an EventBridge event once every minutes using the smallest amount of RAM possible, and taking (hopefully) only a short amount of time.  Timeout is set to 10 seconds...  This will result in free tier usage of Lambda.  Logs will flow to cloudwatch.
