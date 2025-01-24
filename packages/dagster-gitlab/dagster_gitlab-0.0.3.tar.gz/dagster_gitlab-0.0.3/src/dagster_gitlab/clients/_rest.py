from typing import TYPE_CHECKING, Any

import gitlab
import gitlab.base
import gitlab.v4
import gitlab.v4.objects

from dagster_gitlab._utils.type_guards import is_rest_object_subclass


class GitlabRest:
    def __init__(
        self,
        token: str,
        url: str,
        default_project_id: int | None,
        *,
        ssl_verify: bool,
        **kwargs: Any,  # noqa: ANN401, ARG002
    ) -> None:
        self.url = url
        self._client = gitlab.Gitlab(
            url=url, private_token=token, ssl_verify=ssl_verify
        )
        self._default_project_id = default_project_id

    def _get_project_id(self, project_id: int | None) -> gitlab.v4.objects.Project:
        if project_id is not None:
            return self._client.projects.get(
                id=project_id,
            )

        if self._default_project_id is None:
            msg = "Either project_id or deafult_project_id must not be None."
            raise ValueError(msg)

        return self._client.projects.get(
            id=self._default_project_id,
        )

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
        project = self._get_project_id(project_id=project_id)
        mr = project.mergerequests.create(
            data={
                "source_branch": source_branch,
                "target_branch": target_branch,
                "title": title,
                "description": description,
                "labels": labels,
                "remove_source_branch": remove_source_branch,
            }
        )

        if not is_rest_object_subclass(
            mr, gitlab.v4.objects.merge_requests.ProjectMergeRequest
        ):
            msg = f"New mr is not ProjectMergeRequest: {type(mr)}"
            raise TypeError(msg)

        return mr.attributes

    def _get_merge_request(
        self, mr_iid: int, project_id: int | None
    ) -> gitlab.v4.objects.ProjectMergeRequest:
        project = self._get_project_id(project_id=project_id)
        return project.mergerequests.get(id=mr_iid)

    def get_merge_request(self, mr_iid: int, project_id: int | None) -> dict[str, Any]:
        mr = self._get_merge_request(mr_iid=mr_iid, project_id=project_id)
        return mr.attributes

    # TODO: Make `updates` typesafe
    def update_merge_request(
        self, mr_iid: int, updates: dict[str, Any], project_id: int | None
    ) -> dict[str, Any]:
        mr = self._get_merge_request(mr_iid=mr_iid, project_id=project_id)
        for k, v in updates.items():
            setattr(mr, k, v)
        mr.save()
        return mr.attributes

    def close_merge_request(
        self, mr_iid: int, project_id: int | None
    ) -> dict[str, Any]:
        mr = self._get_merge_request(mr_iid=mr_iid, project_id=project_id)
        mr.state_event = "close"
        mr.save()
        return mr.attributes

    def create_issue(
        self, title: str, description: str, *, project_id: int | None = None
    ) -> dict[str, Any]:
        """Create a new issue.

        See `python-gitlab` [issues docs](https://python-gitlab.readthedocs.io/en/stable/gl_objects/issues.html#project-issues)

        Args:
            title: Issue title
            description: Issue descrition
            project_id: Project ID override, uses `default_project_id` if None.

        Raises:
            TypeError: New issue is not `ProjectIssue`

        Returns:
            New issue attributes
        """
        project = self._get_project_id(project_id=project_id)
        issue = project.issues.create(
            data={
                "title": title,
                "description": description,
            }
        )

        if not is_rest_object_subclass(issue, gitlab.v4.objects.issues.ProjectIssue):
            msg = f"New issue is not `ProjectIssue`: {type(issue)}"
            raise TypeError(msg)

        return issue.attributes


if TYPE_CHECKING:
    from dagster_gitlab.protocols import GitlabClient, _dummy_args

    # This uses mypy to confirm GitlabRest implements the GitlabClient protocol.
    _: GitlabClient = GitlabRest(
        token=_dummy_args["token"],
        url=_dummy_args["url"],
        default_project_id=_dummy_args["project_id"],
        ssl_verify=_dummy_args["ssl_verify"],
    )
