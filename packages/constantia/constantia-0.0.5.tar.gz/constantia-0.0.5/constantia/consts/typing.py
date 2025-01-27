from typing import Callable, Literal

VarWatchPredicate = Callable[[str], bool]
OnType = None | list[str] | Literal['uppercase'] | VarWatchPredicate
