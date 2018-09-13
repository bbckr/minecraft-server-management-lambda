import json
import jsonschema


def handler(event, context):

    with open('src/backup/request.schema', 'r') as f:
        schema_data = f.read()
    schema = json.loads(schema_data)

    try:
        jsonschema.validate(event, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as e:
        print(e.message)

    response = {
        "statusCode": 200,
        "body": json.dumps(event)
    }

    return response
