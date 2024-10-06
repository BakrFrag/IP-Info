from jsonschema import validate, ValidationError

SCHEMA = {
    "type": "object",
    "properties": {
        "ips": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "string",
                "minLength": 1,
                "anyOf": [
                    {"format": "ipv4"},
                    {"format": "ipv6"}
                ]
            }
        }
    },
    "required": ["ips"],
    "additionalProperties": False
}

async def validate_ip(text_data: str):
    """
    validate the parsed text is json and include valid IPS
    """
    try:
        validate(instance = text_data, schema = SCHEMA)
    except ValidationError as exc:
        raise ValidationError(exc.message)