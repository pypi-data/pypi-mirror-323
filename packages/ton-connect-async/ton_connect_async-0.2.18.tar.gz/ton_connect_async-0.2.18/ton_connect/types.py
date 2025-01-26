from typing import Annotated

from pydantic import BeforeValidator


def validated_hex_string(v: str | bytes) -> bytes:
    if isinstance(v, bytes):
        return v

    return bytes.fromhex(v)


def validate_int_string(v: str | int) -> str:
    return str(int(v))


HexBytes = Annotated[bytes, BeforeValidator(validated_hex_string)]

IntString = Annotated[str, BeforeValidator(validate_int_string)]
