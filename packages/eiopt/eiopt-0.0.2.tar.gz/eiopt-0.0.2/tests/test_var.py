#!/usr/bin/env python
# -*-coding:utf-8 -*-

import pytest
from eiopt import Variable, Continuous, VariableBase
import numpy as np

def test_Variable():
    var = Variable()
    assert type(var) == Continuous
    assert isinstance (var, Continuous)
    assert isinstance (var, VariableBase)
    assert iter(var)           

def test_Variable_init():
    var = Variable(0)
    assert var._value == 0

    var = Variable([1])
    assert var._value == np.array([1])

    var = Variable([1,2],)
    assert np.array_equal(var._value, np.array([1,2]) )
    assert var[0] == 1
    # test iter mush call two times
    assert max(var) == 2
    assert sum(var) == 3

    var = Variable()
    assert np.isscalar(var._value)

    var = Variable(value=0)
    assert var._value == 0

    var = Variable(value=-1)
    assert var._value == -1

    var = Variable(value=10)
    assert var._value == 10

    var = Variable(value=[5,6])
    assert np.array_equal(var._value, np.array([5,6]) )
    assert var._value.shape == (2,)

    var = Variable(5)
    assert var._value.shape == (5,)
    assert id(var.value[0]) != id(var.value[1])

    var = Variable((5))
    assert var._value.shape == (5,)

    var = Variable((5,6))
    assert var._value.shape == (5,6)

    var = Variable(5,6)
    assert var._value.shape == (5,6)

def test_Variable_compare():
    var = Variable(value=5)
    assert var > 1
    assert var >= 1
    assert var == 5
    assert var <= 7
    assert var < 7

def test_Variable_add():
    var1 = Variable(value=5)
    var2 = Variable(value=4)
    var1 += var2
    assert var1._value == 9


    var1 = Variable(value=[1,2])
    var2 = Variable(value=[1,4])
    var3 = var1 + var2
    assert np.array_equal(var3._value, np.array([2,6]) )

def test_Variable_pow():
    var1 = Variable(value=5)
    var1 = var1 ** 2
    assert var1._value == 25


    var1 = Variable(value=1)
    var2 = Variable(value=2)
    var3 = (var1 + var2)**2
    assert np.array_equal(var3._value, 9)

def test_to_pyomo():
    var1 = Variable(value=5)
    print(f"{var1.to_pyomo()}")
