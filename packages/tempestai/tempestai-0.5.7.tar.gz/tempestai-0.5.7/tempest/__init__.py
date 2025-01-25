import warnings
__version__ = "0.5.7"

warnings.simplefilter('always', DeprecationWarning)

warnings.warn(
    "This python package is deprecated will be removed soon. Please migrate to `langtxt`. Install it with `pip install langtxt`",
    category=DeprecationWarning,
    stacklevel=2
)
