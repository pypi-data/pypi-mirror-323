#!/usr/bin/env python
# -*-coding:utf-8 -*-

import pytest
from eiopt import Objective
from eiopt import Variable


def test_Objective():
    obj = Objective()
    assert type(obj) == Objective

    x = 1
    obj = Objective(x**2)
    assert obj(3) == 1
    
    x = 1
    obj = Objective(lambda x:x**2)
    assert obj(3) == 9
    assert obj(7) == 49

    obj = Objective(lambda x,y:x**2+y)
    assert obj(3, 1) == 10
   
    def test_var(x,y):
        return sum(x) + sum(y)
 
    obj = Objective(test_var)
    assert obj([3], [1]) == 4

    def test_var(x, y):
        return x + y
    obj = Objective(rule=test_var)
    assert obj(3, 1) == 4


def test_Objective_model():
    class TModel():
        x = 2
    model = TModel()
    obj = Objective(lambda model:model.x**2, model=model)
    assert obj() == 4


def test_Objective_var():
    x = Variable(value=1)
    with pytest.raises(ValueError):
        obj = Objective(x**2)

    obj = Objective(lambda x: x**2)
    assert obj(2) == 4

def test_Objective_pyomo():
    obj = Objective(lambda x: x**2)
    assert obj.to_pyomo()._sense == 1

