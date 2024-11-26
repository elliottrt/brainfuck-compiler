
from typing import Callable, Any

Options = dict[str, Any]
JumpPair = tuple[int, int]
Program = list[str]
CodeSegment = list[str]
CodeArguments = list[str]
CodeHeader = Callable[[Options], CodeSegment]
CodeFooter = Callable[[Options], CodeSegment]
CodeCommand = Callable[[str, CodeArguments, Options], CodeSegment]
