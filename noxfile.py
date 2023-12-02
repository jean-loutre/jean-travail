"""Nox configuration file"""
from typing import Callable

from nox import Session
from nox import session as nox_session


def session(
    *tags: str, python: list[str] | None = None
) -> Callable[[Callable[[Session], None]], Callable[[Session], None]]:
    return nox_session(reuse_venv=True, tags=list(tags), python=python)


locations = ["jtravail", "tests"]


# linting
@session("lint", "checks")
def black(session: Session) -> None:
    """Check black formatting."""
    session.install("black")
    session.run("black", "--check", *locations)


@session("lint", "checks")
def isort(session: Session) -> None:
    """Check imports sorting"""
    session.install("isort")
    session.run("isort", "--check", *locations)


@session("lint", "checks")
def flake8(session: Session) -> None:
    """Run flake8"""
    session.install("flake8")
    session.run("flake8")


@session("lint", "checks")
def mypy(session: Session) -> None:
    """Run Mypy"""
    session.install(
        "-e", ".", "mypy", "types-appdirs", "types-click", "types-freezegun"
    )
    session.run("mypy", *locations)


@session("checks", "tests", python=["3.11"])
def unit_tests(session: Session) -> None:
    """Run unit tests."""
    session.install(
        "-e", ".", "pytest", "pytest-cov", "pytest-datadir", "pyfakefs", "freezegun"
    )
    session.run("python", "-m", "pytest", "--cov=jtravail", "--cov-report=html")
