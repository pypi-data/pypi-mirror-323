from dagster_gitlab.clients._graphql import GitlabGraphQL
from dagster_gitlab.clients._rest import GitlabRest

__all__ = [
    "GitlabGraphQL",
    "GitlabRest",
]
