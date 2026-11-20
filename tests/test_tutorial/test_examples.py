import os
import subprocess
import sys
from pathlib import Path

import pytest

DOCS_SRC = Path(__file__).parents[2] / "docs_src"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    # one interpreter per example: SQLModel keeps a single, global table registry
    return subprocess.run(
        [sys.executable, *args],
        cwd=DOCS_SRC,
        env={**os.environ, "PYTHONPATH": str(DOCS_SRC)},
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.mark.parametrize(
    ("example", "output"),
    [
        (
            "quickstart.py",
            ["hero-0 hero-0 in disguise team-0", "[1, 1, 1]", "True"],
        ),
        (
            "create.py",
            [
                "1 team-0",
                "2 Preventers",
                "[('hero-0', 30), ('hero-1', 30)]",
                "Rusty-Man in disguise Avengers",
            ],
        ),
        ("subfactory.py", ["['team-0', 'team-1']", "True", "Z-Force"]),
        ("get_or_create.py", ["True Sharp Tower", "1"]),
        ("build.py", ["None hero-0 team-0", "[('hero-1', 48), ('hero-2', 48)]"]),
    ],
)
def test_example_prints(example: str, output: list[str]) -> None:
    result = run(example)

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == output


def test_pytest_example_passes() -> None:
    result = run("-m", "pytest", "-q", "-p", "no:cacheprovider", "pytest_fixtures")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "2 passed" in result.stdout
