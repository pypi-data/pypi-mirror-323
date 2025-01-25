#!/usr/bin/env python
# -*-coding:utf-8 -*-

import pytest
import eiopt
from eiopt import GA
from eiopt.model import Model
from eiopt.objective import Objective
from eiopt.variables.var_base import Variable

def test_passing():
    model = Model()
    model.x = Variable(100, lb=0, ub=30)
    model.obj1 = Objective(lambda model: sum(model.x))
    result = GA(model=model, generations=50).solve()
    print(result)




