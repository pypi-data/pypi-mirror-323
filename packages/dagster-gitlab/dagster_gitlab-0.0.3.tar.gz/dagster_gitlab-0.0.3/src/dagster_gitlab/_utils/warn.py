import warnings
from collections.abc import Generator
from contextlib import contextmanager, nullcontext


class ExperimentalWarning(Warning):
    pass


@contextmanager
def wrap_warnings(*, ignore: bool = True) -> Generator[None, None, None]:
    if ignore:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=ExperimentalWarning)
            yield
    else:
        with nullcontext():
            yield


def experimental_warning(obj: object) -> None:
    msg = f"{obj!r} is marked as experimental in `python-gitlab` SDK"
    warnings.warn(message=msg, category=ExperimentalWarning, stacklevel=2)
