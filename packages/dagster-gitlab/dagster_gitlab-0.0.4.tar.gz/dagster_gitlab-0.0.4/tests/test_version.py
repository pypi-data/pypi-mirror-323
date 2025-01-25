from importlib.metadata import version

from dagster_gitlab import __version__


def test_distribution_and_import_package_version_equals() -> None:
    assert version("dagster-gitlab") == __version__
