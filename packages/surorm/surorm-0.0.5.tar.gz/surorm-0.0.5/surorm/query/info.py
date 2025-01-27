from typing import Self, Literal

from .types import Expression, Renderable
from .utils import render


type InfoTarget = Literal['root', 'namespace', 'database', 'table']


class Info(Renderable):
    def __init__(self, target: InfoTarget, *args, **kwargs):
        self._target = target

    def sql(self) -> str:
        stmt = [f'info for {self._target}']
        return ' '.join(stmt)
