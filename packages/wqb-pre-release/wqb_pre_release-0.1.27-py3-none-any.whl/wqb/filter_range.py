from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from math import inf, isinf
from typing import Self

__all__ = ['FilterRange']

_isinf = isinf
isinf = lambda x: isinstance(x, float) and _isinf(x)


@dataclass(frozen=True, slots=True)
class FilterRange:

    lo: int | float | datetime = field(default=-inf, kw_only=False)
    hi: int | float | datetime = field(default=inf, kw_only=False)
    lo_eq: bool = field(default=True, kw_only=False)
    hi_eq: bool = field(default=True, kw_only=False)

    def __post_init__(
        self,
    ) -> None:
        if not self.lo <= self.hi:
            raise ValueError(f"not <{self.lo=}> <= <{self.hi=}>")
        if self.lo == self.hi and not (self.lo_eq and self.hi_eq):
            raise ValueError(
                f"<{self.lo=}> == <{self.hi=}> and not (<{self.lo_eq=}> and <{self.hi_eq=}>)"
            )
        if isinf(self.lo) and self.lo_eq:
            raise ValueError(f"isinf(<{self.lo=}>) and <{self.lo_eq=}>")
        if isinf(self.hi) and self.hi_eq:
            raise ValueError(f"isinf(<{self.hi=}>) and <{self.hi_eq=}>")

    @classmethod
    def from_str(
        cls,
        target: str,
    ) -> Self:
        pair = target.split(sep=',')
        if 2 != len(pair):
            raise ValueError(f"More than one ',' occured in '{target}'.")
        lft = pair[0].strip()
        rit = pair[1].strip()
        if lft[0] not in '[(':
            raise ValueError(f"'{lft[0]}' is invalid in '{lft}' in '{target}'.")
        if rit[-1] not in '])':
            raise ValueError(f"'{rit[-1]}' is invalid in '{rit}' in '{target}'.")
        lo_eq = '[' == lft[0]
        hi_eq = ']' == rit[-1]
        lo = lft[1:].lstrip()
        hi = rit[:-1].rstrip()
        try:
            lo = datetime.fromisoformat(lo)
            hi = datetime.fromisoformat(hi)
        except ValueError as e:
            if lo[0] not in '+-':
                lo = '+' + lo
            if hi[0] not in '+-':
                hi = '+' + hi
            lo_abs = lo[1:].lstrip()
            hi_abs = hi[1:].lstrip()
            lo_abs = float(lo_abs) if 'inf' == lo_abs or '.' in lo_abs else int(lo_abs)
            hi_abs = float(hi_abs) if 'inf' == hi_abs or '.' in hi_abs else int(hi_abs)
            lo = -lo_abs if '-' == lo[0] else lo_abs
            hi = -hi_abs if '-' == hi[0] else hi_abs
        return cls(lo, hi, lo_eq, hi_eq)

    @classmethod
    def from_conditions(
        self,
        target: Iterable[str],
    ) -> Self:
        raise NotImplementedError()

    @classmethod
    def parse(
        cls,
        target: str | Iterable[str],
    ) -> Self:
        if isinstance(target, str):
            return cls.from_str(target)
        if isinstance(target, Iterable):
            return cls.from_conditions(target)

    def to_str(
        self,
    ) -> str:
        return ', '.join(
            ('[' if self.lo_eq else '(')
            + (self.lo.isoformat() if isinstance(self.lo, datetime) else str(self.lo)),
            (self.hi.isoformat() if isinstance(self.hi, datetime) else str(self.hi))
            + (']' if self.hi_eq else ')'),
        )

    def to_conditions(
        self,
        *,
        inf_as: object | None = None,
        try_eq: bool = True,
    ) -> list[str]:
        if try_eq and self.lo == self.hi:
            return ['=' + self.lo]
        conditions = []
        if not (isinf(self.lo) and inf_as is None):
            conditions.append(
                ('>=' if self.lo_eq else '>')
                + (
                    self.lo.isoformat()
                    if isinstance(self.lo, datetime)
                    else str(inf_as if isinf(self.lo) else self.lo)
                )
            )
        if not (isinf(self.hi) and inf_as is None):
            conditions.append(
                ('<=' if self.hi_eq else '<')
                + (
                    self.hi.isoformat()
                    if isinstance(self.hi, datetime)
                    else str(inf_as if isinf(self.hi) else self.hi)
                )
            )
        return conditions

    def to_params(
        self,
        whose: str,
        **kwargs,
    ) -> str:
        return '&'.join(
            (whose + condition for condition in self.to_conditions(**kwargs))
        )
