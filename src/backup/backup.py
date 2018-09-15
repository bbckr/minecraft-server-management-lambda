import logging.config
import logging
import json
import yaml
import jsonschema


def setup_logging(default_path='src/shared/logging.yaml', default_level=logging.INFO):
    with open(default_path, 'rt') as f:
        try:
            config = yaml.safe_load(f.read())
            logging.config.dictConfig(config)
        except Exception:
            logging.basicConfig(level=default_level)
            logging.error('Failed to setup custom logger, using default', exc_info=True)
            raise


def validate_request(payload, default_schema='src/backup/request.schema', default_format_checker=jsonschema.FormatChecker()):
    with open(default_schema, 'r') as f:
        try:
            schema_data = f.read()
            schema = json.loads(schema_data)
            jsonschema.validate(payload, schema, format_checker=default_format_checker)
        except jsonschema.exceptions.ValidationError:
            logging.error('JSON request payload failed validation', exc_info=True)
            raise


def handler(event, context):
    try:
        setup_logging()
        validate_request(event)
    except jsonschema.exceptions.ValidationError as e:
        return { 'statusCode': 400, 'body': e.message }
    except Exception as e:
        return { 'statusCode': 500, 'body': 'Internal error' }

    return { 'statusCode': 200, 'body': 'Successfully backed up %s' % event['host'] }
