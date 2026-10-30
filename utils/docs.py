import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).parent.parent
bmsspy_init = root / "bmsspy" / "__init__.py"

VERSION = "2.3.0"
OLD_DOC_VERSIONS = ["2.2.2", "2.1.1", "2.0.1"]

env = {
    **os.environ,
    "version_options": " ".join([VERSION] + OLD_DOC_VERSIONS),
}


def generate_docs(version):
    out_dir = str(root / "docs" / version)
    template_dir = str(root / "doc_template")

    if version != "./" and version != VERSION:
        # Use an isolated environment per old version so their (older)
        # dependencies don't clobber the current venv.
        tarball = str(root / "dist" / f"bmsspy-{version}.tar.gz")
        subprocess.run(
            [
                "uv", "run", "--isolated",
                "--with", tarball,
                "--with", "pdoc",
                "pdoc", "-o", out_dir, "-t", template_dir, "bmsspy",
            ],
            check=True,
            env=env,
            cwd=str(root),
        )
    else:
        subprocess.run(
            [sys.executable, "-m", "pdoc", "-o", out_dir, "-t", template_dir, "bmsspy"],
            check=True,
            env=env,
        )


# Build __init__.py from README
readme = (root / "README.md").read_text()
import_string = """
from bmsspy.entrypoint import Bmssp
from bmsspy.helpers.utils import has_cpp, cpp_check

try:
    from bmsspy.cpp import BmsspC
except ImportError:
    class BmsspC:  # type: ignore
        def __init__(self, *args, **kwargs):
            raise ImportError(
                "C++ implementation 'BmsspC' is not available. Please install the C++ supported wheels or build the C++ extension."
            )

"""
bmsspy_init.write_text(f'r"""\n{readme}\n"""\n\n{import_string}\n')

generate_docs("./")
generate_docs(VERSION)
for version in OLD_DOC_VERSIONS:
    generate_docs(version)
