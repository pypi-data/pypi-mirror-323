from typing import TypeGuard, TypeVar

import gitlab

T = TypeVar("T", bound=gitlab.base.RESTObject)


def is_rest_object_subclass(
    obj: gitlab.base.RESTObject,
    subclass: type[T],
) -> TypeGuard[T]:
    return isinstance(obj, subclass)
