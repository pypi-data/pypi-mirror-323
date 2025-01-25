# Home

This library provides an integration with GitLab for Dagster.

!!! note

    This project is **not** affiliated with Dagster.

It provides a thin wrapper around the `python-gitlab` SDK with a REST or GraphQL client.
It integrates with convienient Dagster features by providing configurable resources and run sensors so that you can alert and control GitLab issues from Dagster.

## Installation

```sh
pip install dagster-gitlab
```

## Example

An [example Dagster project hosted on GitLab](https://gitlab.com/cooperellidge/test-dagster) is used for testing and demonstration purposes.

```python
from dagster import asset
from dagster_gitlab import GitlabResource


@asset
def my_asset(gitlab: GitlabResource) -> None:
    gitlab.get_client().create_issue(
        title="Dagster's first GitLab issue",
        description="This example is taken from dagster-github",
    )

defs = Definitions(
    assets=[my_asset],
    resources={
        "gitlab": GitlabResource(
            token=EnvVar("GITLAB_PROJECT_ACCESS_TOKEN"),
            url=EnvVar("GITLAB_URL"),
            project_id=IntEnvVar("GITLAB_DEFAULT_PROJECT_ID"),
        )
    },
)
```

## Inspiration

It is inspired largely by `dagster-github` for the resources, and `dagster-slack` and `dagster-msteams` for the sensors.

The library is intended to be familiar for Dagster users that have used those other integrations, while remaining familiar to GitLab users.

## Versioning

The project does not follow SemVer.
For the foreseeable future, it will always be behind the official Dagster integrations version.

- **Major** - not planning on bumping this
- **Minor** - what most projects would consider "major", along with large feature sets
- **Patch** - Any small change, including some new features and bug fixes

## Roadmap

- `v0.1` is targeting feature parity with `dagster-github` using the REST client
- `v0.2` is targeting feature similarity with `dagster-slack` and `dagster-msteams`
- `v0.3` is targeting feature parity with `dagster-github` using the GraphQL client
