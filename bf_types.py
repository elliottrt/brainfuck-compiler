from typing import *
from types import *

Options = Dict[str, Any]
JumpPair = Tuple[int, int]
Program = List[str]
CodeSegment = List[str]
CodeArguments = List[str]
CodeHeader = Callable[[Options], CodeSegment]
CodeFooter = Callable[[Options], CodeSegment]
CodeCommand = Callable[[str, CodeArguments, Options], CodeSegment]
