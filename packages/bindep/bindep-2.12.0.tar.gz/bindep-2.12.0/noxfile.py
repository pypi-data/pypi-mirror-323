import nox


nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["tests-3", "linters"]


# Note setting python this way seems to give us a target name without
# python specific suffixes while still allowing us to force a specific
# version using --force-python.
@nox.session(python="3")
def linters(session):
    session.install("hacking>=7,<8")
    session.run("flake8")


@nox.session(python="3")
def docs(session):
    session.install("-r", "requirements.txt")
    session.install("-r", "doc/requirements.txt")
    session.install(".")
    session.run(
        "sphinx-build", "-W",
        "-d", "doc/build/doctrees",
        "-b", "html",
        "doc/source/", "doc/build/html"
    )


@nox.session(python="3")
def venv(session):
    session.install("-r", "requirements.txt")
    session.install("-r", "test-requirements.txt")
    session.install("-e", ".")
    session.run(*session.posargs)


# This will attempt to run python3 tests by default.
@nox.session(python=["3"])
def tests(session):
    session.install("-r", "requirements.txt")
    session.install("-r", "test-requirements.txt")
    session.install("-e", ".")
    session.run("stestr", "run", *session.posargs)
    session.run("stestr", "slowest")


@nox.session(python="3")
def cover(session):
    session.install("-r", "requirements.txt")
    session.install("-r", "test-requirements.txt")
    session.install("-e", ".")
    session.env["PYTHON"] = "coverage run --source bindep --parallel-mode"
    session.run("stestr", "run", *session.posargs)
    session.run("stestr", "slowest")
    session.run("coverage", "combine")
    session.run("coverage", "html", "-d", "cover")
    session.run("coverage", "xml", "-o", "cover/coverage.xml")
