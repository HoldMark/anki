from pathlib import Path


def find_root():
    path = Path(__file__).resolve()

    for parent in [path, *path.parents]:
        if (parent / "pyproject.toml").exists():
            return parent.resolve()


ROOT_PATH = find_root()
LOGS_PATH = ROOT_PATH / "logs"
