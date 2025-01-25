import os
from pathlib import Path

# Automatically set SERENITY_RESOURCES
package_dir = Path(__file__).resolve().parent.parent
resources_dir = package_dir / "share" / "serenity" / "data"
if resources_dir.exists():
    os.environ["SERENITY_RESOURCES"] = str(resources_dir) + "/"

laplace_dir = package_dir / "share" / "laplace"
if laplace_dir.exists():
    os.environ["LAPLACE_ROOT"] = str(laplace_dir)

from .greetings import greetings
from .fragment import fragment

__all__ = ["greetings", "fragment"]