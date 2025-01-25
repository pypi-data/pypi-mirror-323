from .common import *
from .variables import VariableBase
import pyomo.environ as pyo
from typing import Callable

class Objective:
    """
    Objective(rule, sense=1)
    sense:
    """
    def __init__(self, 
                 rule : Callable = lambda model: model, 
                 sense: int = minimize, 
                 name: str = "",
                 model=None):
        if callable(rule):
            self._rule = rule
        elif isinstance(rule, VariableBase):
            raise ValueError(
                """
                Please input function rather than expression,
                   for example: lambda model: model.x + model.y
                """
            )
        else:
            self._rule = lambda *args, **kwargs: rule
        self.sense = sense
        self.name = name
        self.model = model

    @property
    def rule(self):
        return self._rule

    @rule.setter
    def rule(self, value):
        self._rule = value

    def __call__(self, *args, **kwargs):
        if (args == () and kwargs == {}):
            if self.model is not None:
                return self._rule(self.model)
        return self._rule(*args, **kwargs)

    def to_pyomo(self):
        return pyo.Objective(rule=self._rule, sense=self.sense)
