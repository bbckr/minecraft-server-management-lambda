# Minecraft Server Management through Lambda Functions

## Developing locally
``` bash
docker-compose run --rm dev
```

## Deploying the Infrastructure
The exported environment variables below will be configured to the terraform AWS provider when you apply. There is no need to specify it in the provider.

On `terraform apply`, the resources required to deploy a lambda function (s3, iam, lambda) are created and the zip file is uploaded to s3 and deployed to lambda.
``` bash
# Step 1: Run the development container locally. This container has all the dependencies needed
#         to build, package, and deploy the infrastructure.
# Note: If you rather deveop on your own machine, ensure python, virtualenv, terraform, and serverless
# are installed
docker-compose run --rm dev

# Step 2: Export the AWS keys required to deploy to AWS
#         https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html
export AWS_ACCESS_KEY_ID=XXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXX

# Step 3: Export the private key that will be used to ssh into the server by the lambda function
#         The public key must have been added to the server prior
export TF_VAR_PRIVATE_KEY=XXXXXX

# Step 4: Run these make commands individually, or simply run `make all`:

# Builds the terraform code to deploy from the jinja templates and serverless.yml
make build

# Individually packages each function defined in the serverless.yml
make package

# Deploys the terraform code
make deploy
```
