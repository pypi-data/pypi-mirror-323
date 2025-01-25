from typing import Sequence, Union, Type
from dataclasses import dataclass


@dataclass(frozen=True)
class Parameter:
    """
    A parameter name and value to replace a string token in a protocol file with.

    For example, Parameter('some_name', int, 123) would replace the instance of '''parameter: some_name''' with 123
    within the contents of a protocol file.
    """
    PREFIX = "'''parameter: "
    SUFFIX = "'''"

    name: str
    type: Union[Type[int], Type[float], Type[str], Type[list], Type[tuple], Type[dict]]
    value: Union[int, float, str, list, tuple, dict]

    @staticmethod
    def is_safe_str(string: str) -> bool:
        """
        Checks string can't escape quotes.
        """
        return '"' not in string

    def __post_init__(self):
        if not type(self.value) is self.type:
            raise ValueError(f'expected type "{self.type}" but got {type(self.value)}')

        # Prevent code injection
        if self.type is str and not self.is_safe_str(self.value):
            raise ValueError('string cannot contain double quote character')

    @property
    def token_b(self) -> bytes:
        """
        The full token with quotes, as bytes, e.g. b'''parameter: some_name'''.
        """
        return f"{self.PREFIX}{self.name}{self.SUFFIX}".encode()

    @property
    def value_b(self) -> bytes:
        """
        The value as bytes.
        """
        if self.type is str:
            return f'"{self.value}"'.encode()
        return f'{self.value}'.encode()


def inject_parameters(protocol: bytes, params: Sequence[Parameter]) -> bytes:
    """
    Replaces parameter tokens with their values in a protocol, as bytes, as a means of dynamically enabling parameters
    to be injected into an otherwise fixed parameter file.
    :param protocol: The protocol code as bytes to insert parameters into.
    :param params: The parameters to insert.
    """
    for param in params:
        # Check exactly one of each token exists
        count = protocol.count(param.token_b)
        if count != 1:
            raise ValueError(f'expected 1 occurrence of "{param.token_b}", but got {count} occurrences')

        # Replace parameter tokens
        protocol = protocol.replace(param.token_b, param.value_b)

    # Check no parameters were missed
    if Parameter.PREFIX.encode() in protocol:
        raise ValueError('it appears not all parameters were replaced')

    return protocol
