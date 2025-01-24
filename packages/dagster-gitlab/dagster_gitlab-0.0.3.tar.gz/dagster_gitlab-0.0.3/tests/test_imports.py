# ruff: noqa: F401, I001


def test_import_clients_toplevel() -> None:
    from dagster_gitlab import GitlabRest
    from dagster_gitlab import GitlabGraphQL


def test_import_clients_module() -> None:
    from dagster_gitlab.clients import GitlabRest
    from dagster_gitlab.clients import GitlabGraphQL


def test_import_protocols_toplevel() -> None:
    from dagster_gitlab import GitlabClient


def test_import_protocols_module() -> None:
    from dagster_gitlab.protocols import GitlabClient


def test_import_resources_toplevel() -> None:
    from dagster_gitlab import GitlabResource


def test_import_resources_module() -> None:
    from dagster_gitlab.resources import GitlabResource


def test_import_sensors_toplevel() -> None:
    from dagster_gitlab import gitlab_on_failure
    from dagster_gitlab import gitlab_on_success
    from dagster_gitlab import make_gitlab_on_run_failure_sensor


def test_import_sensors_module() -> None:
    from dagster_gitlab.sensors import gitlab_on_failure
    from dagster_gitlab.sensors import gitlab_on_success
    from dagster_gitlab.sensors import make_gitlab_on_run_failure_sensor
