from dagster_gitlab.clients import GitlabRest
from dagster_gitlab.resources import GitlabResource
from dagster_gitlab.sensors import (
    gitlab_on_failure,
    gitlab_on_success,
    make_gitlab_on_run_failure_sensor,
)

__version__ = "0.0.4"

__all__ = [
    "GitlabResource",
    "GitlabRest",
    "gitlab_on_failure",
    "gitlab_on_success",
    "make_gitlab_on_run_failure_sensor",
]

# These are more project related todos, rather than features.
# TODO: Initial implementation of core features
# TODO: remove noqas
# TODO: write docs
# TODO: GH Pages
# TODO: test PyPI
# TODO: GH Actions publish
# TODO: PyPI
