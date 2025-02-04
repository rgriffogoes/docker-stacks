# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

import logging

import pytest  # type: ignore
from pathlib import Path

from conftest import TrackedContainer

LOGGER = logging.getLogger(__name__)
THIS_DIR = Path(__file__).parent.resolve()


@pytest.mark.parametrize(
    "test_file",
    # TODO: add local_sparklyr
    ["local_pyspark", "local_spylon", "local_sparkR", "issue_1168"],
)
def test_nbconvert(container: TrackedContainer, test_file: str) -> None:
    """Check if Spark notebooks can be executed"""
    host_data_dir = THIS_DIR / "data"
    cont_data_dir = "/home/jovyan/data"
    output_dir = "/tmp"
    conversion_timeout_ms = 600
    LOGGER.info(f"Test that {test_file} notebook can be executed ...")
    command = (
        "jupyter nbconvert --to markdown "
        + f"--ExecutePreprocessor.timeout={conversion_timeout_ms} "
        + f"--output-dir {output_dir} "
        + f"--execute {cont_data_dir}/{test_file}.ipynb"
    )
    logs = container.run_and_wait(
        timeout=60,
        no_warnings=False,
        volumes={str(host_data_dir): {"bind": cont_data_dir, "mode": "ro"}},
        tty=True,
        command=["start.sh", "bash", "-c", command],
    )
    warnings = TrackedContainer.get_warnings(logs)
    # Some Spark warnings
    assert len(warnings) == 5

    expected_file = f"{output_dir}/{test_file}.md"
    assert expected_file in logs, f"Expected file {expected_file} not generated"
