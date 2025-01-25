import warnings

__version__ = "0.5.3"

warnings.simplefilter('always', category=DeprecationWarning)

warnings.warn(
    "This package is deprecated ('tempestai') will be removed soon."
    "Please migrate to `alpine-index`. 'pip install alpine-index'",
    category=DeprecationWarning,
    stacklevel=2
)
