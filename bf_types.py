
from typing import Callable
from argparse import Namespace


Options = Namespace
JumpPair = tuple[int, int]
Program = list[str]
CodeSegment = list[str]
CodeArguments = list[str]
CodeHeader = Callable[[Options], CodeSegment]
CodeFooter = Callable[[Options], CodeSegment]
CodeCommand = Callable[[str, CodeArguments, Options], CodeSegment]
