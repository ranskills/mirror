from collections.abc import Mapping


def validate_required_fields(fields: Mapping[str, str | int | float], message_template: str):
    for field, value in fields.items():
        if not value:
            raise ValueError(message_template.format(field=field))
