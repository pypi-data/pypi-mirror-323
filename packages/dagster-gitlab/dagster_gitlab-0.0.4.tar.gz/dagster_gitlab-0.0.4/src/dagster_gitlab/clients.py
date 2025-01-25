from typing import Any

import gitlab
import gitlab.base
import gitlab.v4
import gitlab.v4.objects

from dagster_gitlab._utils.type_guards import is_rest_object_subclass


class GitlabRest:
    """A GitLab API wrapper using the v4 REST API.

    This client provides convience functions for common GitLab workflows.
    """

    def __init__(
        self,
        token: str,
        url: str,
        default_project_id: int | None,
        *,
        ssl_verify: bool = True,
    ) -> None:
        """A GitLab API wrapper using the v4 REST API.

        Args:
            token: GitLab access token with suitable permissions for the project
            url: Fully-specifed URL to the GitLab host, excluding the project namespace
            default_project_id: Default project ID for workflows
            ssl_verify: Whether SSL certificates should be validated.
        """
        self.url = url
        self._client = gitlab.Gitlab(
            url=url, private_token=token, ssl_verify=ssl_verify
        )
        self._default_project_id = default_project_id

    def _get_project(self, project_id: int | None) -> gitlab.v4.objects.Project:
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
        """Create a merge request.

        Args:
            source_branch: _description_
            target_branch: _description_
            title: _description_
            description: _description_. Defaults to None.
            labels: _description_. Defaults to None.
            project_id: _description_. Defaults to None.
            remove_source_branch: _description_. Defaults to False.

        Raises:
            TypeError: _description_

        Returns:
            _description_
        """
        project = self._get_project(project_id=project_id)
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

        if not is_rest_object_subclass(mr, gitlab.v4.objects.ProjectMergeRequest):
            msg = f"Expected `ProjectMergeRequest` from GitLab SDK, got {type(mr)}"
            raise TypeError(msg)

        return mr.attributes

    def _get_merge_request(
        self, iid: int, project_id: int | None
    ) -> gitlab.v4.objects.ProjectMergeRequest:
        project = self._get_project(project_id=project_id)
        return project.mergerequests.get(id=iid)

    def get_merge_request(self, iid: int, project_id: int | None) -> dict[str, Any]:
        """Get a merge request.

        Args:
            iid: _description_
            project_id: _description_

        Returns:
            _description_
        """
        mr = self._get_merge_request(iid=iid, project_id=project_id)
        return mr.attributes

    def update_merge_request(
        self, iid: int, updates: dict[str, Any], project_id: int | None
    ) -> dict[str, Any]:
        """Update a merge request.

        Args:
            iid: _description_
            updates: _description_
            project_id: _description_

        Returns:
            _description_
        """
        mr = self._get_merge_request(iid=iid, project_id=project_id)
        for k, v in updates.items():
            setattr(mr, k, v)
        mr.save()
        return mr.attributes

    def close_merge_request(self, iid: int, project_id: int | None) -> dict[str, Any]:
        """Close a merge request.

        Args:
            iid: _description_
            project_id: _description_

        Returns:
            _description_
        """
        mr = self._get_merge_request(iid=iid, project_id=project_id)
        mr.state_event = "close"
        mr.save()
        return mr.attributes

    # Issues

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
            TypeError: Expected `ProjectIssue` from GitLab SDK

        Returns:
            New issue attributes
        """
        project = self._get_project(project_id=project_id)
        issue = project.issues.create(
            data={
                "title": title,
                "description": description,
            }
        )

        if not is_rest_object_subclass(issue, gitlab.v4.objects.ProjectIssue):
            msg = f"Expected `ProjectIssue` from GitLab SDK, got {type(issue)}"
            raise TypeError(msg)

        return issue.attributes

    def _get_issue(
        self, iid: int, project_id: int | None
    ) -> gitlab.v4.objects.ProjectIssue:
        project = self._get_project(project_id=project_id)
        return project.issues.get(id=iid)

    def get_issue(self, iid: int, project_id: int | None) -> dict[str, Any]:
        """Get an issue.

        Args:
            iid: _description_
            project_id: _description_

        Returns:
            _description_
        """
        issue = self._get_issue(iid=iid, project_id=project_id)
        return issue.attributes

    def update_issue(
        self, iid: int, updates: dict[str, Any], project_id: int | None
    ) -> dict[str, Any]:
        """Update an issue.

        Args:
            iid: _description_
            updates: _description_
            project_id: _description_

        Returns:
            _description_
        """
        issue = self._get_issue(iid=iid, project_id=project_id)
        for k, v in updates.items():
            setattr(issue, k, v)
        issue.save()
        return issue.attributes

    def close_issue(self, iid: int, project_id: int | None = None) -> dict[str, Any]:
        """Close an issue.

        Args:
            iid: _description_
            project_id: _description_. Defaults to None.

        Returns:
            _description_
        """
        issue = self._get_issue(iid=iid, project_id=project_id)
        issue.state_event = "close"
        issue.save()
        return issue.attributes

    # Create issue note

    def create_issue_note(
        self, iid: int, body: str, project_id: int | None
    ) -> dict[str, Any]:
        """Create a note on an issue.

        Args:
            iid: _description_
            body: _description_
            project_id: _description_

        Returns:
            _description_
        """
        issue = self._get_issue(iid=iid, project_id=project_id)

        note = issue.notes.create(data={"body": body})

        if not is_rest_object_subclass(issue, gitlab.v4.objects.ProjectIssueNote):
            msg = f"Expected `ProjectIssue` from GitLab SDK, got {type(issue)}"
            raise TypeError(msg)

        return note.attributes
