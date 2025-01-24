# ruff: noqa: ARG002

import warnings
from typing import TYPE_CHECKING, Any


class GitlabGraphQL:
    url: str

    def __init__(
        self,
        token: str,
        url: str,
        default_project_id: int | None,
        *,
        ssl_verify: bool,
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        warnings.warn(
            message="GraphQL API is marked as experimental in `python-gitlab` SDK.",
            stacklevel=2,
        )

        msg = "Method not yet implemented."
        raise NotImplementedError(msg)

    # # Issues
    def create_issue(
        self, title: str, description: str, *, project_id: int | None = None
    ) -> dict[str, Any]:
        msg = "Method not yet implemented."
        raise NotImplementedError(msg)

    # Merge Requests
    def create_merge_request(  # noqa: PLR0913
        self,
        source_branch: str,
        target_branch: str,
        title: str,
        description: str | None = None,
        labels: list[str] | None = None,
        project_id: int | None = None,
        *,
        remove_source_branch: bool = False,
    ) -> dict[str, Any]:
        msg = "Method not yet implemented."
        raise NotImplementedError(msg)

    def get_merge_request(self, mr_iid: int, project_id: int | None) -> dict[str, Any]:
        msg = "Method not yet implemented."
        raise NotImplementedError(msg)

    def update_merge_request(
        self, mr_iid: int, updates: dict[str, Any], project_id: int | None
    ) -> dict[str, Any]:
        msg = "Method not yet implemented."
        raise NotImplementedError(msg)

    def close_merge_request(
        self, mr_iid: int, project_id: int | None
    ) -> dict[str, Any]:
        msg = "Method not yet implemented."
        raise NotImplementedError(msg)


if TYPE_CHECKING:
    from dagster_gitlab.protocols import GitlabClient, _dummy_args

    # This uses mypy to confirm GitlabRest implements the GitlabClient protocol.
    _: GitlabClient = GitlabGraphQL(
        token=_dummy_args["token"],
        url=_dummy_args["url"],
        default_project_id=_dummy_args["project_id"],
        ssl_verify=_dummy_args["ssl_verify"],
    )
