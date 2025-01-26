import pytest
from eiopt import Model
from eiopt import Variable
from eiopt import Objective
from eiopt import Constraint

def test_pyomo():
    model = Model()
    model.x = Variable()
    model.y = Variable()
    model.obj = Objective(lambda model: model.x + model.y)
    model.con = Constraint(lambda model: model.x>5)
    model.con = Constraint(lambda model: 2*model.y>4)
    model.solve_by_lp()
    # assert type(model) == Model
    # assert hasattr(model, "variables")


