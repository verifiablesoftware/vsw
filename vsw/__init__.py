__all__ = (
    "__title__",
    "__summary__",
    "__uri__",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    "__copyright__",
)

__copyright__ = "Copyright 2020 VSW contributors"

import sys

if sys.version_info[:2] >= (3, 8):
    from importlib import metadata as importlib_metadata
else:
    import importlib_metadata


metadata = importlib_metadata.metadata("vsw")


__title__ = metadata["name"]
__summary__ = metadata["summary"]
__uri__ = metadata["home-page"]
__version__ = metadata["version"]
__author__ = metadata["author"]
__email__ = metadata["author-email"]
__license__ = metadata["license"]
