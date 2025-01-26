import os


def maybe_find_docode_project_dir() -> str | None:
    try:
        return find_docode_project_dir()
    except Exception:
        return None


def find_docode_project_dir():
    maybe_pyproject = os.path.join(os.path.abspath("."), "pyproject.toml")
    while not os.path.isfile(maybe_pyproject):
        prev_pyproject = maybe_pyproject
        maybe_pyproject = os.path.join(
            os.path.dirname(os.path.dirname(maybe_pyproject)), "pyproject.toml"
        )
        if prev_pyproject == maybe_pyproject:
            break
    if os.path.isfile(maybe_pyproject):
        return os.path.dirname(maybe_pyproject)
    raise FileNotFoundError("No project dir found.")
