from __future__ import annotations

import shutil
from pathlib import Path

import nox

DIR = Path(__file__).parent.resolve()

nox.options.sessions = ["lint", "pylint", "tests"]

conda_sess = lambda **kw: nox.session(
    venv_backend="conda",
    # does not work with environment yml
    venv_params=["--file", "conda_environment.txt"],
    # don't reinstall the environment, not very fast
    reuse_venv=True,
    **kw,
)


@conda_sess(name="lint_conda")
def lint(session: nox.Session) -> None:
    """Run the linter."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", *session.posargs)


@conda_sess()
def poetry(session: nox.Session) -> None:
    """Add a new dependency."""
    session.install("poetry")  # nox -s poetry -- add requests
    session.run("poetry", *session.posargs)


@conda_sess(name="pylint_conda")
def pylint(session: nox.Session) -> None:
    """Run PyLint."""
    session.install("-e", ".", "--no-deps")
    session.install("pylint")
    session.run("pylint", "src", *session.posargs)


@nox.session
def tests(session: nox.Session) -> None:
    """
    Run the unit and regular tests.
    """
    session.install(".[test]")
    session.run("pytest", *session.posargs)


@nox.session
def coverage(session: nox.Session) -> None:
    """
    Run tests and compute coverage.
    """

    session.posargs.append("--cov=tk-sciproj-test")
    tests(session)


@nox.session
def docs(session: nox.Session) -> None:
    """
    Build the docs. Pass "serve" to serve.
    """

    session.install(".[docs]")
    session.chdir("docs")
    session.run("sphinx-build", "-M", "html", ".", "_build")

    if session.posargs:
        if "serve" in session.posargs:
            print("Launching docs at http://localhost:8000/ - use Ctrl-C to quit")
            session.run("python", "-m", "http.server", "8000", "-d", "_build/html")
        else:
            session.warn("Unsupported argument to docs")


@nox.session
def build(session: nox.Session) -> None:
    """
    Build an SDist and wheel.
    """

    build_p = DIR.joinpath("build")
    if build_p.exists():
        shutil.rmtree(build_p)

    session.install("build")
    session.install("conda")
    session.run("conda", "env", "create", "-f", "environment.yml")
    session.run("python", "-m", "build")
