from typing import Any, overload

from dagster import ConfigurableResource

from dagster_gitlab import GitlabClient, GitlabGraphQL, GitlabRest
from dagster_gitlab._utils.enums import ClientType
from dagster_gitlab._utils.warn import experimental_warning, wrap_warnings


class GitlabResource(ConfigurableResource):  # noqa: D101
    token: str
    url: str
    project_id: int | None
    client_type: ClientType = ClientType.REST
    ssl_verify: bool = True
    ignore_experimental: bool = False

    def __post_init__(self) -> None:
        with wrap_warnings(ignore=self.ignore_experimental):
            if self.client_type is ClientType.GRAPHQL:
                experimental_warning(obj=GitlabGraphQL)

    # These overloads are used to says that kwargs are only allowed with a custom_client
    @overload
    def get_client(
        self,
    ) -> GitlabClient: ...
    @overload
    def get_client(
        self,
        custom_client: type[GitlabClient],
        **kwargs: Any,  # noqa: ANN401
    ) -> GitlabClient: ...
    def get_client(  # noqa: D102
        self,
        custom_client: type[GitlabClient] | None = None,
        **kwargs: Any,
    ) -> GitlabClient:
        kwargs = {
            "token": self.token,
            "url": self.url,
            "default_project_id": self.project_id,
            "ssl_verify": self.ssl_verify,
            **kwargs,
        }

        if custom_client is not None:
            return custom_client(**kwargs)

        match self.client_type:
            case ClientType.REST:
                return GitlabRest(**kwargs)
            case ClientType.GRAPHQL:
                with wrap_warnings(ignore=self.ignore_experimental):
                    return GitlabGraphQL(**kwargs)
