# Minecraft Server Management through Lambda Functions

## Developing locally
``` bash
docker-compose run --rm dev
```

## Deploying the Infrastructure
The exported environment variables below will be configured to the terraform AWS provider when you apply. There is no need to specify it in the provider.

On `terraform apply`, the resources required to deploy a lambda function (s3, iam, lambda) are created and the zip file is uploaded to s3 and deployed to lambda.
``` bash
# Required steps before deploying to AWS
# https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
export AWS_ACCESS_KEY_ID=XXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXX

# The serverless cli is only used for packaging, and the function must be packaged before you can deploy it
serverless package

# For first time set-up
terraform init terraform/

# Apply
terraform apply --auto-approve terraform/
```
