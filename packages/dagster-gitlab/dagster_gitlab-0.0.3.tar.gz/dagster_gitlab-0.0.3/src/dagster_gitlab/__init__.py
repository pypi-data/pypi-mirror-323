from dagster_gitlab.clients._graphql import GitlabGraphQL
from dagster_gitlab.clients._rest import GitlabRest
from dagster_gitlab.protocols import GitlabClient
from dagster_gitlab.resources import GitlabResource
from dagster_gitlab.sensors import (
    gitlab_on_failure,
    gitlab_on_success,
    make_gitlab_on_run_failure_sensor,
)

__all__ = [
    "GitlabClient",
    "GitlabGraphQL",
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
