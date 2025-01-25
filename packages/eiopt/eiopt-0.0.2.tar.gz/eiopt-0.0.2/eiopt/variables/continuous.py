from ..common import *
from .var_base import VariableBase
import numpy as np
import pyomo.environ as pyo


@VARIABLES.register_module()
class Continuous(VariableBase):
    def __init__(self, *shape, **kwargs):
        VariableBase.__init__(self, *shape, **kwargs)
        self.type = "C"

    def uniform(self, value=None):
        if value is not None:
            return np.random.random(self.shape)
        else:
            lb = self.lb if self.lb != -np.inf else -99999999
            ub = self.ub if self.ub != np.inf else 99999999
            return np.random.uniform(lb, ub, size=self.shape)

    def init_value(self, value=None):
        if value is not None:
            if np.isscalar(value) and (self.shape == (1,) ):
                self.value = value
            elif np.array(value).shape != self.shape:
                raise ValueError(
                    f"error shape for value shape : {value.shape} and shape {self.shape}"
                )
            else:
                self.value = np.array(value)
        else:
            lb = self.lb if self.lb != -np.inf else -99999999
            ub = self.ub if self.ub != np.inf else 99999999
            self.value = np.random.uniform(lb, ub, size=self.shape)
            if self.shape == (1,):
                self.value = self.value[0]

    def get_shape(self, value):
        shape = len(self.value_value())
        if isinstance(self.shape, tuple):
            value_shape = value.shape
        if value_shape != self.shape:
            raise ValueError(
                f"error shape for value shape : {value_shape} and shape {self.shape}"
            ) from None
        return shape

    def check(self, value):
        if not isinstance(value, (np.ndarray)):
            return False
        if value < self.lb:
            return False
        if value > self.ub:
            return False
        if self.shape != value.shape:
            return False
        if not np.isscalar(value):
            return False
        return True

    def to_pyomo(self):
        return pyo.Var(within=pyo.NonNegativeReals)
