from dataclasses import dataclass

from dacite import from_dict, Config


def test_from_dict_with_spinal_case():
    @dataclass
    class X:
        my_value: int

    result = from_dict(X, {"my-value": 1}, Config(strict=True))

    assert result == X(my_value=1)
