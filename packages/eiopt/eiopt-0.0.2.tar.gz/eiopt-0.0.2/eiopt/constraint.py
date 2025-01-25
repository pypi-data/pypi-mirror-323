from .common import *
from .variables import VariableBase
import pyomo.environ as pyo
import inspect
import ast

def extract_lambda_functions(source_code):
    tree = ast.parse(source_code)
    lambdas = []

    class LambdaVisitor(ast.NodeVisitor):
        def visit_Lambda(self, node):
            lambdas.append(ast.unparse(node))
            self.generic_visit(node)

    LambdaVisitor().visit(tree)
    return lambdas


class Constraint:
    """
    Constraint(rule, name="")
    sense: 
    """
    def __init__(self, 
                 rule: int=1, 
                 direction: enumerate="<=",  
                 # ["=", "<=", ">=", ">", "<"]
                 bound: int= 0,
                 name: str="",
                 model=None):
        self.direction = direction.strip()
        self.bound = bound
        if callable(rule):
            self.rule = rule
            source_code = inspect.getsource(self.rule)
            lambda_code = extract_lambda_functions(source_code.strip())[0]
            rule_str = lambda_code.replace("\n", "") 
            for symbol in [">=", "<=", "==", "<", ">"]:
                if symbol in rule_str:
                    rule_list = rule_str.split(symbol)
                    if len(rule_list) != 2:
                        raise ValueError(f"Please input right lambda function")
                    self._rule = eval(rule_list[0].strip())
                    self.rule_str = rule_list[0].strip()
                    self.direction = symbol
                    self.bound = eval(rule_list[1].strip())
                    break
        elif isinstance(rule, VariableBase):
            raise ValueError(f"Please input function rather than expression")
        else:
            self._rule = lambda *args, **kwargs:rule
        self.name = name
        self.epsilon = 1e-9
        if self.direction in ["<", ">"]:
            self.bound += self.epsilon
            if self.direction == "<":
                self.bound -= 2*self.epsilon
            self.direction += "="
        # 0 Equality Constraints  1 for Inequality constraints
        self.ctype = 0 if direction in ["=", "=="] else 1
        self.model = model
        self.pyomo_rule = eval(f"lambda model: rule(model) {self.direction} {self.bound}")
        
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
        try:
            source_code = inspect.getsource(self.rule)
            lambda_code = extract_lambda_functions(source_code.strip())[0]
            rule_str = lambda_code.replace("\n", "") 
            rule_str += f"{self.direction} {self.bound}"
            self.pyomo_rule = eval(rule_str)
        except Exception as e:
            print(e)
            try:
                rule_str = self.rule_str + f"{self.direction} {self.bound}"
                self.pyomo_rule = eval(rule_str) 
            except Exception as e1:
                raise ValueError("error rule") from e1
        return pyo.Constraint(rule=self.pyomo_rule)

    def to_pymoo(self):
        try:
            source_code = inspect.getsource(self.rule)
            lambda_code = extract_lambda_functions(source_code.strip())[0]
            rule_str = lambda_code.replace("\n", "") 
        except Exception as e:
            try:
                rule_str = self.rule_str + f"{self.direction} {self.bound}"
            except Exception as e1:
                raise ValueError("error rule") from e1
        
        if self.direction != "==":
            # g(x) <= 0
            if self.direction == "<=":
                rule_str = rule_str.replace(":", ": max(")
                rule_str += f"- {self.bound}, 0)"
            else:
                rule_str = rule_str.replace(":", ": -min(")
                rule_str += f"- {self.bound}, 0)"
        else:
            # h(x) == 0
            rule_str += f"{self.direction} {self.bound}"
        self.g_rule = eval(rule_str)
        return pyo.Constraint(rule=self.g_rule)