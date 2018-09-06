# TODO: Include terraform as part of pipeline
variable lambda_name {
  default = "minecraft-service"
}

provider "aws" {
  version = "~> 1.29.0"
  region  = "us-east-1"
}

resource "aws_s3_bucket" "lambda_bucket" {
  bucket = "lambda-bucket-${var.lambda_name}"
  acl    = "private"
}

# TODO: Templatize s3 object, iam role, and lambda function creation with Jinja
resource "aws_iam_role" "lambda_function_role_backup" {
  name = "lambda-function-role-backup"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_s3_bucket_object" "lambda_function_zip_backup" {
  bucket = "${aws_s3_bucket.lambda_bucket.id}"
  key    = "1.0.0/backup.zip"
  source = ".serverless/backup.zip"
  etag   = "${md5(file(".serverless/backup.zip"))}"
}

resource "aws_lambda_function" "lambda_function_backup" {
  function_name = "backup"
  s3_bucket     = "${aws_s3_bucket.lambda_bucket.id}"
  s3_key        = "1.0.0/backup.zip"
  handler       = "src/backup/handler.backup"
  runtime       = "python2.7"
  role          = "${aws_iam_role.lambda_function_role_backup.arn}"
}
