import pytest
from eiopt import Model
from eiopt import Variable
from eiopt import Objective, maximize
from eiopt import Constraint
import pyomo.environ as pyo
from jsonschema import validate

def test_model():
    model = Model()
    assert type(model) == Model
    assert hasattr(model, "variables")


def test_model_var():
    model = Model()
    model.x = Variable()
    assert model.variables == [model.x]
    assert model.x.name == "x"

    with pytest.raises(ValueError):
        model.addVariable()

    model.addVariable(name="y")
    assert model.variables == [model.x, model.y]

    with pytest.raises(ValueError):
        model.addVariable(name="y")

    model.addVariable(name="z")
    assert model.variables == [model.x, model.y, model.z]

def test_model_obj():
    model = Model()
    model.x = Variable(value=3)
    model.obj1 = Objective(lambda model: model.x**2)
    assert model.objectives == [model.obj1]
    assert model.obj1() == 9

    obj2 = model.addObjective(lambda model: model.x**2+1)
    assert model.objectives == [model.obj1, obj2]
    assert model.objectives[1]() == 10
    # model.addObjective(name="obj2", rule="x**2")
    # print(model.objectives)


def test_model_con():
    model = Model()
    model.x = Variable(value=3)
    model.con1 = Constraint(lambda model: model.x>1)
    assert model.constraints == [model.con1]
    assert model.con1() == 3

    con2 = model.addConstraint(lambda model: model.x*2<9)
    assert model.constraints == [model.con1, con2]
    assert con2() == 6

def test_pyomo():
    model = Model()
    assert type(model.to_pyomo()) == pyo.ConcreteModel


def test_solve_by_pyomo():
    model = Model()
    model.x = Variable()
    model.y = Variable()
    model.obj = Objective(lambda model: model.x +  model.y ** 2)
    model.con = Constraint(lambda model: model.x>=5)
    model.con = Constraint(lambda model: 2*model.y>=4)
    result = model.solve()
    print(result)

def test_solve_by_pyomo1():
    model = Model()
    model.x1 = Variable()
    model.x2 = Variable()
    model.obj = Objective(lambda model: 4*model.x1 +  3*model.x2, sense=maximize)
    model.con = Constraint(lambda model: 2*model.x1 + model.x2 <= 10)
    model.con = Constraint(lambda model: model.x1 + model.x2 <= 8 )
    model.con = Constraint(lambda model: model.x2 <= 7)
    result = model.solve()
    print(result)


def test_solve_by_pyomo2():
    model = Model()
    model.x1 = Variable()
    model.x2 = Variable()
    model.obj = Objective(lambda model: 4*model.x1 +  3*model.x2, sense=maximize)
    model.con = Constraint(lambda model: 2*model.x1 + model.x2, "<=", 10)
    model.con = Constraint(lambda model: model.x1 + model.x2, "<=", 8 )
    model.con = Constraint(lambda model: model.x2, "<=", 7)
    result = model.solve()
    print(result)

def test_solve_by_pyomo_func():
    model = Model()
    model.x1 = Variable()
    model.x2 = Variable()
    def obj(model):
        return 4*model.x1 +  3*model.x2
    def con1(model):
        return 2*model.x1 + model.x2
    def con2(model):
        return model.x1 + model.x2 <= 8
    model.obj = Objective(obj, sense=maximize)
    model.con1 = Constraint(con1, "<=", 10)
    model.con2 = Constraint(con2)
    model.con3 = Constraint(lambda model: model.x2, "<=", 7)
    result = model.solve()
    print(result)

def test_solve_by_moo():
    model = Model()
    model.x = Variable(2)
    model.obj1 = Objective(lambda model: sum(model.x))
    model.obj2 = Objective(lambda model: max(model.x))
    model.con1 = Constraint(lambda model: model.x[0] > 5 )
    model.con2 = Constraint(lambda model: 2*sum(model.x) > 200 )
    model.con3 = Constraint(lambda model: model.x[0] > 0 )
    model.con4 = Constraint(lambda model: model.x[1] > 0 )
    assert model.ieq_constraints == [model.con1, model.con2, model.con3, model.con4]
    result = model.solve()
    print(result)

def test_solve_by_moo_bnh():
    model = Model()
    model.x = Variable(2, lb=[0,0], ub=[5,3])
    model.obj1 = Objective(lambda model:  4*model.x[0]**2 + 4*model.x[1]**2)
    model.obj2 = Objective(lambda model: (model.x[0]-5)**2 + (model.x[1]-5)**2)
    model.g1 = Constraint(lambda model: (model.x[0]-5)**2 + model.x[1]**2 <= 25)
    model.g2 = Constraint(lambda model: (model.x[0]-8)**2 + (model.x[1]+3)**2 >= 7.7)
    result = model.solve()
    print(result)

def test_solve_by_EA():
    model = Model()
    model.x = Variable(10, lb=0, ub=30)
    model.obj1 = Objective(lambda model: sum(model.x)) #, sense=-1
    result = model.solve(solver="GA", generations=300)
    print(result)

schema = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["optimal", "suboptimal", "no solution," "no boundary"]
        },
        "message": {
            "type": "string"
        },
        "objective": {
            "oneOf": [
                {
                    "type": "number"
                },
                {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            ]
        },
        "gap": {
            "oneOf": [
                {
                    "type": "number"
                },
                {
                    "type": "array",
                    "items": {
                        "type": "number"
                    }
                }
            ]
        },
        "var": {
            "type": "object",
            "patternProperties": {
                "^[a-zA-Z0-9]+$": {
                    "type": "number"
                }
            },
            "additionalProperties": True
        }
    },
    "required": ["status", "message", "objective", "gap", "var"]
}

import numpy as np

def test_result_schema():
    data = {
        'status': 'optimal', 
        'message': 'Model was solved to optimality (subject to tolerances), and an optimal solution is available.', 
        'objective': 9.0, 
        'gap': 0.0, 
        'var': {
            'x2': 5.0, 
            'x3': 2.0
        }
    }
    validate(instance=data, schema=schema)
    data = {
        'status': 'optimal', 
        'message': 'Model was solved to optimality (subject to tolerances), and an optimal solution is available.', 
        'objective': np.inf, 
        'gap': [], 
        'var': {
            'x2': 5.0, 
            'x3': 2.0
        }
    }
    validate(instance=data, schema=schema)
