# minecraft-server-management-lambda
This project is an example of:
1. Developing applications in a docker container
2. Repeatably deploying lambda infrastructure using terraform, jinja, and serverless
3. Interacting with SSM parameters using Lambda for secrets
4. Applying least priviledge IAM policies per lambda function
5. Backing up files on remote servers and docker containers using Lambda functions (doesn't have to be minecraft servers, I just use it for my own)

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

## Usage Documentation

### Backup

#### Assumptions
1. The server host has ssh enabled
2. The server or docker container you are backing up files on has zip installed

#### Parameters
``` js
{
  /* required parameters */
  "host": "x", // minecraft server url
  "source": ["/x/x.txt", "/x/x_dir/"], // absolute path of files and folders to backup
  "dest": "/x/dir/", // absolute path to store the zip on the host server

  /* optional parameters */
  "port": 22,// (default: 22) ssh port to use when connecting
  "user": "x", // (default: root) ssh user to use when connecting
  "upload": false, // (default: false) uploads to the bucket under /backups
  "container": "x" // specify the container name if you are backing up files from a docker container running on the server
}
```

Example request if you deployed the minecraft server from the `minecraft-server-docker` repository [here](https://github.com/bbckr/minecraft-server-docker):
``` js
{
  "host": "minecraft.towerofswole.com",
  "source": ["/server/tos_world/", "/server/whitelist.txt"],
  "dest": "/tmp",
  "upload": true,
  "container": "minecraft"
}
```
