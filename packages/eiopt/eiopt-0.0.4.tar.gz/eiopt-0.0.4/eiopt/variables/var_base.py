from abc import abstractmethod
import copy
import numpy as np
from ..common import *
import pyomo.environ as pyo


class VariableBase:
    def __init__(self, *shape, **kwargs):
        '''
        Args:
            shape: tuple, shape of the variable
            value: np.ndarray, value of the variable
            lb: float, lower bound of the variable
            ub: float, upper bound of the variable
            name: str, name of the variable
        Example:
            Scalar:
                VariableBase(1) for value = 1
            Array or Vector:
                VariableBase([1, 2, 3]) for value = [1, 2, 3]
            Matrix or Tensor:
                VariableBase(2,3) or VariableBase((2,3)) 
                for value = np.random.random((2,3))
        '''
        if not shape:
            self.shape = (1,)
            if "value" in kwargs:
                value = kwargs.pop("value", None)
                self.shape = np.array(value).shape
        else:
            if isinstance(shape, tuple) and len(shape):
                if not is_single_level_tuple(shape):
                    if isinstance(shape[0], tuple):
                        self.shape = shape[0]
                    else:
                        value = np.array(shape[0])
                        self.shape = value.shape
                elif shape == (0,):
                    self.shape = (1,)
                    value = 0
                else:
                    self.shape = shape
        if "value" not in locals():
            value = kwargs.pop("value", None)
        self.lb = kwargs.pop('lb', -np.inf)
        self.ub = kwargs.pop('ub', np.inf)
        self.name = kwargs.pop('name', "")
        self.type = "B"
        self.init_value(value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @abstractmethod
    def init_value(self):
        pass

    def __add__(self, other):
        if isinstance(other, VariableBase):
            return VariableBase(self.value + other.value)
        if isinstance(other, (int, float)):
            return self.value + other
        return NotImplemented

    def __radd__(self, other: any) -> 'Person':
        """
        添加右操作方法
        """
        return self.__add__(other)
    
    def set_value(self, value):
        self._value = value

    @abstractmethod
    def to_pyomo(self):
        pass

    def __eq__(self, other):
        if isinstance(other, VariableBase):
            return self.value == other.value
        if isinstance(other, (int, float)):
            return self.value == other
        return NotImplemented

    # 特殊方法：长度运算
    def __len__(self):
        return 1

    # 特殊方法：一元运算
    def __neg__(self):
        return VariableBase(-self.value)

    # 特殊方法：反算术运算
    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return -self.__sub__(other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rtruediv__(self, other):
        return 1 / self.__truediv__(other)

    # 特殊方法：算术运算
    def __add__(self, other):
        if isinstance(other, VariableBase):
            return Variable(value=self.value + other.value, vtype=self.type)
        if isinstance(other, (int, float)):
            return Variable(value=self.value + other, vtype=self.type)
        return NotImplemented

    def __sub__(self, other):
        if isinstance(other, VariableBase):
            return Variable(value=self.value - other.value)
        if isinstance(other, (int, float)):
            return Variable(value=self.value - other)
        return NotImplemented

    def __mul__(self, other):
        if isinstance(other, VariableBase):
            return Variable(value=self.value * other.value, vtype=self.type)
        if isinstance(other, (int, float)):
            return Variable(value=self.value * other, vtype=self.type)
        return NotImplemented

    def __pow__(self, other, modulo=None):
        try:
            if isinstance(other, VariableBase):
                result = Variable(value=self._value ** other.value)
            else:
                result = Variable(value=self._value ** other, vtype=self.type)
            if modulo is not None:
                result %= modulo
            return result
        except Exception as e:
            return NotImplemented

    def check_le(self, value):
        violate = self.value - value
        if violate > 0:
            return violate
        return np.array([0])

    def __lt__(self, other):
        if isinstance(other, (int, float)):
            return self.value < other
        return self.__le__(other)

    def __le__(self, other):
        if isinstance(other, VariableBase):
            return self.check_le(other.value)
        if isinstance(other, (int, float)):
            return self.value <= other
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, (int, float)):
            return self.value > other
        return self.__ge__(other)

    def check_ge(self, value):
        violate = value - self.value
        if violate > 0:
            return violate
        return np.array([0])

    def __ge__(self, other):
        if isinstance(other, VariableBase):
            return self.check_ge(other.value)
        if isinstance(other, (int, float)):
            return self.value >= other
        return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, VariableBase):
            return Variable(self.value / other.value)
        return NotImplemented

    # 特殊方法：获取对象的字符串表示

    def __str__(self):
        return f"VariableBase with value: {self.value}"

    # 特殊方法：获取对象的详细字符串表示
    def __repr__(self):
        return f"VariableBase(value={self.value})"

    def __deepcopy__(self, memo):
        new_instance = Variable(**self.__dict__)
        return new_instance

    def __getitem__(self, key):
        try:
            return self.value[key]
        except :
            return self.value
        
    def __iter__(self):
        self.index = 0
        return self

    # 特殊方法：迭代
    # def __iter__(self):
    #     self.index = 0
    #     return iter([self.value])

    def __next__(self):
        if not hasattr(self, "index"):
            self.index = 0
        if isinstance(self.value, (int, float)):
            if self.index:
                raise StopIteration
            else:
                self.index = 1
                return self.value
        if self.index >= len(self.value):
            raise StopIteration
        else:
            value = self.value[self.index]
            self.index += 1
            return value


def Variable(*args, **kwargs):
    # Pretend to be a class
    vtype = kwargs.pop('vtype', "C")
    if len(vtype) == 1:
        vtype = vtype_map.get(vtype, vtype)
    vtype = vtype.lower()
    try:
        return VARIABLES.module_dict[vtype](*args, **kwargs)
    except Exception as e:
        raise ValueError(f"Unsupported type: {vtype}") from e
