import ipaddress
from jsonschema import validate, ValidationError, FormatChecker

format_checker = FormatChecker()

@format_checker.checks("ipv4")
def is_ipv4(instance):
    """
    validate against ipv4
    make sure parsed ip is public ip not of type [reserved, loopback, private]
    """
    try:
        ip = ipaddress.IPv4Address(instance)
        return not (ip.is_private or ip.is_reserved or ip.is_loopback)
    except ValueError:
        return False


@format_checker.checks("ipv6")
def is_ipv6(instance):
    """
    validate against ipv6
    make sure parsed ip is public ip not of type [reserved, loopback, private]
    """
    try:
        ip = ipaddress.IPv6Address(instance)
        return not (ip.is_private or ip.is_reserved or ip.is_loopback)
    except ValueError:
        return False
    

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
        validate(instance = text_data, schema = SCHEMA, format_checker = format_checker)
    except ValidationError as exc:
        raise ValidationError(exc.message)