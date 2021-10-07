from dataclasses import is_dataclass
from functools import lru_cache
from itertools import zip_longest
from typing import Any, Dict, Mapping, Optional, Type, TypeVar, get_type_hints

from dacite.config import Config
from dacite.dataclasses import (
    DefaultValueNotFoundError,
    create_instance,
    get_default_value_for_field,
    get_fields,
)
from dacite.exceptions import (
    DaciteError,
    DaciteFieldError,
    ForwardReferenceError,
    MissingValueError,
    StrictUnionMatchError,
    UnexpectedDataError,
    UnionMatchError,
    WrongTypeError,
)
from dacite.types import (
    extract_generic,
    extract_init_var,
    extract_origin_collection,
    is_generic_collection,
    is_init_var,
    is_instance,
    is_optional,
    is_union,
    transform_value,
)

T = TypeVar("T")


@lru_cache
def _get_type_hints(obj: Any) -> Mapping[str, Any]:
    try:
        return get_type_hints(obj=obj)
    except NameError as error:
        raise ForwardReferenceError(str(error))


def from_dict(data_class: Type[T], data: Mapping[str, Any], config: Optional[Config] = None) -> T:
    """Create a data class instance from a dictionary.

    :param data_class: a data class type
    :param data: a dictionary of a input data
    :param config: a configuration of the creation process
    :return: an instance of a data class
    """
    if any(("-" in k for k in data.keys())):
        data = {k.replace("-", "_"): v for k, v in data.items()}
    init_values: Dict[str, Any] = {}
    post_init_values: Dict[str, Any] = {}
    config = config or Config()
    if config.forward_references is None:
        data_class_hints = _get_type_hints(data_class)
    else:
        data_class_hints = get_type_hints(data_class, globalns=config.forward_references)
    data_class_fields = get_fields(data_class)
    if config.strict:
        extra_fields = (
            set(data.keys())
            - {config.rename_map.get(f.name, f.name) for f in data_class_fields}
            - {f.name for f in data_class_fields}
        )
        if extra_fields:
            raise UnexpectedDataError(keys=extra_fields)
    for field in data_class_fields:
        field_type = data_class_hints[field.name]
        field_name_data = config.rename_map.get(field.name, field.name)
        if field_name_data in data or field.name in data:
            try:
                field_data = data.get(field_name_data)
                if field_data is None:
                    field_data = data[field.name]
                transformed_value = transform_value(
                    type_hooks=config.type_hooks, cast=config.cast, target_type=field_type, value=field_data
                )
                value = _build_value(type_=field_type, data=transformed_value, config=config)
            except DaciteFieldError as error:
                error.update_path(field.name)
                raise
            if config.check_types and not is_instance(value, field_type):
                raise WrongTypeError(field_path=field.name, field_type=field_type, value=value)
        else:
            try:
                value = get_default_value_for_field(field=field, field_type=field_type)
            except DefaultValueNotFoundError:
                if not field.init:
                    continue
                raise MissingValueError(field.name)
        if field.init:
            init_values[field.name] = value
        else:
            post_init_values[field.name] = value

    return create_instance(data_class=data_class, init_values=init_values, post_init_values=post_init_values)


def _build_value(type_: Type, data: Any, config: Config) -> Any:
    if is_init_var(type_):
        type_ = extract_init_var(type_)
    if is_union(type_):
        return _build_value_for_union(union=type_, data=data, config=config)
    elif is_generic_collection(type_) and is_instance(data, extract_origin_collection(type_)):
        return _build_value_for_collection(collection=type_, data=data, config=config)
    elif is_dataclass(type_) and isinstance(data, Mapping):
        return from_dict(data_class=type_, data=data, config=config)
    return data


def _build_value_for_union(union: Type, data: Any, config: Config) -> Any:
    types = extract_generic(union)
    if is_optional(union) and len(types) == 2:
        return _build_value(type_=types[0], data=data, config=config)
    union_matches = {}
    for inner_type in types:
        try:
            # noinspection PyBroadException
            try:
                data = transform_value(
                    type_hooks=config.type_hooks, cast=config.cast, target_type=inner_type, value=data
                )
            except Exception:  # pylint: disable=broad-except
                continue
            value = _build_value(type_=inner_type, data=data, config=config)
            if is_instance(value, inner_type):
                if config.strict_unions_match:
                    union_matches[inner_type] = value
                else:
                    return value
        except DaciteError:
            pass
    if config.strict_unions_match:
        if len(union_matches) > 1:
            raise StrictUnionMatchError(union_matches)
        return union_matches.popitem()[1]
    if not config.check_types:
        return data
    raise UnionMatchError(field_type=union, value=data)


def _build_value_for_collection(collection: Type, data: Any, config: Config) -> Any:
    data_type = data.__class__
    if isinstance(data, Mapping):
        item_type = extract_generic(collection, defaults=(Any, Any))[1]
        return data_type((key, _build_value(type_=item_type, data=value, config=config)) for key, value in data.items())
    elif is_instance(data, tuple):
        types = extract_generic(collection)
        if len(types) == 2 and types[1] == Ellipsis:
            return data_type(_build_value(type_=types[0], data=item, config=config) for item in data)
        return data_type(
            _build_value(type_=type_, data=item, config=config) for item, type_ in zip_longest(data, types)
        )
    item_type = extract_generic(collection, defaults=(Any,))[0]
    return data_type(_build_value(type_=item_type, data=item, config=config) for item in data)
