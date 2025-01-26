from typing import Any, Callable, Dict, Optional, Tuple, Type, Union

from typing_extensions import get_type_hints

_cached_hints: dict[Tuple[Union[Type, Callable], bool], dict[str, Any]] = {}


def cached_get_type_hints(
    obj: Union[Type, Callable],
    include_extras: bool = False,
    globalns: Optional[Dict[str, Any]] = None,
) -> dict[str, Any]:
    k = (obj, include_extras)
    if k in _cached_hints:
        return _cached_hints[k]
    v = _cached_hints[k] = get_type_hints(obj, include_extras=include_extras, globalns=globalns)
    return v
