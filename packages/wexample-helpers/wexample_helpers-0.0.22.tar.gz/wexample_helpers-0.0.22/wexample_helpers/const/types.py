from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Match, Optional, Set, Union

AnyList = List[Any]
StringKeysDict = Dict[str, Any]
StringKeysMapping = Mapping[str, Any]
StringsDict = Dict[str, str]
StringsList = List[str]
SetList = Set[str]
StringsMatch = Match[str]
BasicInlineValue = str | int | float | bool | None
BasicValue = BasicInlineValue | AnyList | StringKeysDict

AnyCallable = Callable[..., Any]
Args = Any
DecoratedCallable = Callable[..., AnyCallable]
Kwargs = Any
ResponsePrintType = Optional[BasicInlineValue | StringKeysDict | AnyList]
StringMessageParameters = StringKeysDict

FileStringOrPath = Union[str, Path]
