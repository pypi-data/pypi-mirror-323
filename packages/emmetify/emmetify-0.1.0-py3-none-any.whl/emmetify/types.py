import sys
from typing import Literal

SupportedFormats = Literal["html"]
DefaultFormat: SupportedFormats = "html"


if sys.version_info >= (3, 10):
    # Python 3.10+ - Use native union operator
    StrOrNoneType = str | None
    IntOrNoneType = int | None
else:
    # Python 3.9 - Use typing.Union
    from typing import Union

    StrOrNoneType = Union[str, None]
    IntOrNoneType = Union[int, None]
