# ruff: noqa: D101, D102, D107
from typing import TYPE_CHECKING, Any, Protocol, TypedDict


# TODO: Implement `lazy` option, maybe with @overload
class GitlabClient(Protocol):
    url: str

    def __init__(
        self,
        token: str,
        url: str,
        default_project_id: int | None,
        *,
        ssl_verify: bool,
        **kwargs: Any,  # noqa: ANN401
    ) -> None: ...

    # # Issues
    def create_issue(
        self, title: str, description: str, *, project_id: int | None = None
    ) -> dict[str, Any]: ...

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
    ) -> dict[str, Any]: ...

    def get_merge_request(
        self, mr_iid: int, project_id: int | None
    ) -> dict[str, Any]: ...

    def update_merge_request(
        self, mr_iid: int, updates: dict[str, Any], project_id: int | None
    ) -> dict[str, Any]: ...

    def close_merge_request(
        self, mr_iid: int, project_id: int | None
    ) -> dict[str, Any]: ...


if TYPE_CHECKING:

    class _ClientArgs(TypedDict):
        token: str
        url: str
        project_id: int
        ssl_verify: bool

    _dummy_args = _ClientArgs(
        token="token",  # noqa: S106
        url="https://gitlab.example.com",
        project_id=1,
        ssl_verify=True,
    )
