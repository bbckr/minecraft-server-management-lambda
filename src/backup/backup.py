from io import StringIO
from pathlib import Path
import socket
import logging.config
import logging
import datetime
import json
import yaml
import jsonschema
import boto3
import botocore
import paramiko


class ValidationException(Exception):
    pass


class ClientException(Exception):
    pass


class InternalException(Exception):
    pass


def setup_logging(path='src/shared/logging.yaml', log_level=logging.INFO):
    try:
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
    except Exception:
        logging.basicConfig(level=log_level)
        logging.error('Failed to setup custom logger, using default', exc_info=True)


def validate_request(
                    payload, schema='src/backup/request.schema',
                    format_checker=jsonschema.FormatChecker()):
    if not Path(schema).is_file():
        message = 'JSON schema missing at path %s' % schema
        logging.error(message)
        raise InternalException(message)

    with open(schema, 'r') as f:
        try:
            schema_data = f.read()
            schema = json.loads(schema_data)
            jsonschema.validate(payload, schema, format_checker=format_checker)
        except jsonschema.exceptions.ValidationError as e:
            logging.error('JSON request payload failed validation', exc_info=True)
            raise ValidationException(e.message)


def establish_connection(host, port, user):
    # Retrieve and create private key
    try:
        client = boto3.client('ssm')
        ssm_parameter = client.get_parameter(Name='PRIVATE_KEY', WithDecryption=True)
        private_key_value = ssm_parameter['Parameter']['Value']
        private_key = paramiko.RSAKey.from_private_key(StringIO(private_key_value))
    except botocore.exceptions.ClientError as e:
        client_error_code = e.response['Error']['Code']
        if client_error_code == 'ParameterNotFound':
            message = 'SSM parameter PRIVATE_KEY does not exist'
        else:
            message = 'SSM Client error %s' % client_error_code
        logging.error(message, exc_info=True)
        raise InternalException(message)
    except paramiko.ssh_exception.SSHException:
        message = 'Invalid private key'
        logging.error(message, exc_info=True)
        raise ClientException(message)

    # Initialize ssh connection
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port=port, username=user, pkey=private_key)
    except socket.gaierror:
        message = 'Unable to resolve host %s' % host
        logging.error(message, exc_info=True)
        raise ClientException(message)
    except paramiko.ssh_exception.NoValidConnectionsError:
        message = 'Unable to connect on port %s' % port
        logging.error(message, exc_info=True)
        raise ClientException(message)
    except paramiko.ssh_exception.AuthenticationException:
        message = 'Unable to authenticate with user %s' % user
        logging.error(message, exc_info=True)
        raise ClientException(message)

    return ssh


def create_backup(ssh, backup_file_name, source, dest, container):
    # Backup files to destination directory
    zip_cmd = 'zip -u %s/%s -r' % (dest, backup_file_name) if not container \
        else 'docker exec -d %s zip -u /%s -r' % (container, backup_file_name)

    # Make destination directory if it doesnt exist
    ssh.exec_command('mkdir -p %s' % dest)

    for s in source:
        # TODO: error handle if file not found or empty, or container does not exist
        ssh.exec_command('%s %s' % (zip_cmd, s))

    # Move to destination directory in host if container
    if container:
        ssh.exec_command('docker cp %s:/%s %s' % (container, backup_file_name, dest))

    return


def return_response(statusCode, body):
    response = {
        'statusCode': statusCode,
        'body': body
    }

    return response


def handler(event, context):
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M")
    backup_file_name = 'backup_%s_%s.zip' % (timestamp, event.get('host', ''))

    host = event.get('host')
    port = event.get('port', 22)
    user = event.get('user', 'root')

    source = event.get('source')
    dest = event.get('dest')
    container = event.get('container')

    try:
        setup_logging()
        validate_request(event)
        
        ssh = establish_connection(host, port, user)
        create_backup(ssh, backup_file_name, source, dest, container)
        ssh.close()

    except ValidationException as e:
        return return_response(400, str(e))
    except ClientException as e:
        return return_response(400, str(e))
    except InternalException as e:
        return return_response(500, str(e))
    except Exception as e:
        logging.error('Internal Error', exc_info=True)
        return return_response(500, 'Internal Error')

    return return_response(200, 'Successfully backed up %s' % event['host'])
