from dagster import ConfigurableResource

from dagster_gitlab import GitlabRest


class GitlabResource(ConfigurableResource):
    """Configurable Dagster resource to generate a GitLab REST client."""

    token: str
    url: str
    project_id: int | None
    ssl_verify: bool = True

    def get_client(self) -> GitlabRest:
        """Generate a GitLab REST client based on the resource's configuration.

        Returns:
            GitLab REST client.
        """
        return GitlabRest(
            token=self.token,
            url=self.url,
            default_project_id=self.project_id,
            ssl_verify=self.ssl_verify,
        )
