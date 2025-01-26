#!/usr/bin/env python
# -*-coding:utf-8 -*-

import pytest
from eiopt import Constraint
from eiopt import Variable
from eiopt.constraint import extract_lambda_functions
import math


def test_constraint():
    con = Constraint()
    assert type(con) == Constraint

    x = 1
    con = Constraint(lambda x: x>1)
    assert con(3) == 3
    assert con(1) == 1
    assert con(0) == 0

def base_var(x, y):
    return x + y

def test_constraint_func():
    con = Constraint(rule=base_var)
    assert con(3, 1) == 4
    con_fun = con.to_pymoo()
    assert con.g_rule(3, 1) == 4


def test_constraint_var():
    x = Variable(value=1)
    with pytest.raises(ValueError):
        con = Constraint(x**2)

    con = Constraint(lambda x: x**2)
    assert con(2) == 4


def test_constraint_lambda():
    x = Variable(value=1)
    with pytest.raises(ValueError):
        con = Constraint(x**2)

    with pytest.raises(ValueError):
        con = Constraint(lambda x: x**2>5>4)

    con = Constraint(lambda x: x**2 > 9)
    assert con.bound == 9+con.epsilon

    con = Constraint(lambda x: x**2 < 9)
    assert con.bound == 9-con.epsilon

    con = Constraint(lambda x: x**2 )
    assert con.bound == 0
    assert con.direction == "<="

def test_constraint_pyomo():
    rule = lambda x: x
    con = Constraint(rule, ">", 2)
    pyomo_con = con.to_pyomo()
    assert con(3) == 3
    assert con.pyomo_rule(3) == True

    con = Constraint(lambda x: x>2)
    pyomo_con = con.to_pyomo()
    assert con(43) == 43
    assert con.pyomo_rule(6) == True

def test_constraint_pymoo():
    rule = lambda x: x
    con = Constraint(rule, "<=", 2)
    pyomo_con = con.to_pymoo()
    assert con.g_rule(3) == 1
    assert con.g_rule(2) == 0
    assert con.g_rule(1) == 0
    assert con.ctype == 1

    con = Constraint(rule, "<", 2)
    pyomo_con = con.to_pymoo()
    assert math.isclose(con.g_rule(3), 1, abs_tol=con.epsilon)
    assert math.isclose(con.g_rule(2), 0, abs_tol=con.epsilon)
    assert con.g_rule(1) == 0

    con = Constraint(rule, ">=", 2)
    pyomo_con = con.to_pymoo()
    assert con.g_rule(3) == 0
    assert con.g_rule(2) == 0
    assert con.g_rule(1) == 1

    con = Constraint(rule, ">", 2)
    pyomo_con = con.to_pymoo()
    assert con.g_rule(3) == 0
    assert math.isclose(con.g_rule(2), con.epsilon, abs_tol=con.epsilon)
    assert math.isclose(con.g_rule(1), 1+con.epsilon, abs_tol=con.epsilon)

def test_extract_lambda_functions():
    aims = ['lambda x: x * 2']
    assert extract_lambda_functions("lambda x: x * 2") == aims
    assert extract_lambda_functions("lambda_func = lambda x: x * 2") == aims
    assert extract_lambda_functions("Constraint(lambda x: x * 2, '>', 2)") == aims