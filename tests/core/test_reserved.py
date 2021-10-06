from dataclasses import dataclass

from dacite import from_dict, Config


def test_from_dict_with_reserved_field():
    @dataclass
    class X:
        return_: int

    result = from_dict(X, {"return": 1}, Config(strict=True))

    assert result == X(return_=1)


def test_from_dict_with_sanitized_reserved_field():
    @dataclass
    class X:
        return_: int

    result = from_dict(X, {"return_": 1}, Config(strict=True))

    assert result == X(return_=1)
