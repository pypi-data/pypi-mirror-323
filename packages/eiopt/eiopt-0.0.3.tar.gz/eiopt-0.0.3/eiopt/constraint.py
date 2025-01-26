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

def get_function_name(source_code):
    tree = ast.parse(source_code)
    function_name = None

    class FunctionVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            nonlocal function_name
            function_name = node.name
            self.generic_visit(node)

    FunctionVisitor().visit(tree)
    return function_name

def format_function_string(func_str):
    lines = func_str.split('\n')
    min_indent = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
    formatted_lines = [line[min_indent:] if line.strip() else line for line in lines]
    formatted_str = '\n'.join(formatted_lines)
    return formatted_str

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
            if "lambda" in source_code:
                lambda_code = extract_lambda_functions(source_code.strip())[0]
                self.rule_str = lambda_code.rstrip('\n')
            else:
                self.rule_str = format_function_string(source_code).rstrip('\n')
            # split rule_str by symbol
            for symbol in [">=", "<=", "==", "<", ">"]:
                if symbol in self.rule_str:
                    rule_list = self.rule_str.split(symbol)
                    if len(rule_list) != 2:
                        raise ValueError(f"Please input right lambda function")
                    if "lambda" in source_code:
                        self.rule = eval(rule_list[0].strip())
                    else:
                        self.rule = self.get_func(rule_list[0].strip())
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
    
    def to_pyomo_lambda(self):
        try:
            source_code = inspect.getsource(self.rule)
            lambda_code = extract_lambda_functions(source_code.strip())[0]
            rule_str = lambda_code.replace("\n", "") 
            rule_str += f"{self.direction} {self.bound}"
            self.pyomo_rule = eval(rule_str)
        except Exception as e:
            try:
                rule_str = self.rule_str + f"{self.direction} {self.bound}"
                self.pyomo_rule = eval(rule_str) 
            except Exception as e1:
                raise ValueError("error rule") from e1
            
    def get_func(self, rule_str):
        fun_name = get_function_name(rule_str)
        exec(rule_str, {}, globals())
        return globals()[fun_name]

    def to_pyomo_func(self):
        rule_str = self.rule_str + f" {self.direction} {self.bound}"
        # fun_name = get_function_name(rule_str)
        # exec(rule_str, {}, globals())
        # self.pyomo_rule = globals()[fun_name]
        self.pyomo_rule = self.get_func(rule_str)

    def to_pyomo(self):
        if "lambda" in self.rule_str:
            self.to_pyomo_lambda()
        else:
            self.to_pyomo_func()
        return pyo.Constraint(rule=self.pyomo_rule)
            
    def to_pymoo_lambda(self):
        # try:
        #     source_code = inspect.getsource(self.rule).strip()
        #     lambda_code = extract_lambda_functions(source_code)[0]
        #     rule_str = lambda_code.replace("\n", "") 
        # except Exception as e:
        #     try:
        #         rule_str = self.rule_str + f"{self.direction} {self.bound}"
        #     except Exception as e1:
        #         raise ValueError("error rule") from e1
        # rule_str = self.rule_str + f"{self.direction} {self.bound}"
        if self.direction != "==":
            # g(x) <= 0
            if self.direction == "<=":
                rule_str = self.rule_str.replace(":", ": max(")
                rule_str += f"- {self.bound}, 0)"
            else:
                rule_str = self.rule_str.replace(":", ": -min(")
                rule_str += f"- {self.bound}, 0)"
        else:
            # h(x) == 0
            rule_str = self.rule_str + f"{self.direction} {self.bound}"
        return rule_str
    
    def to_pymoo_func(self):
        if self.direction != "==":
            # g(x) <= 0
            if self.direction == "<=":
                rule_str = self.rule_str.replace("return ", "return max(").rstrip('\n')
                rule_str += f"- {self.bound}, 0)"
            else:
                rule_str = self.rule_str.replace("return", "return -min(").rstrip('\n')
                rule_str += f"- {self.bound}, 0)"
        else:
            # h(x) == 0
            rule_str = self.rule_str + f"{self.direction} {self.bound}"
        return rule_str

    def to_pymoo(self):
        if "lambda" in self.rule_str:
            rule_str = self.to_pymoo_lambda()
            self.g_rule = eval(rule_str)
        else:
            rule_str = self.to_pymoo_func()
            fun_name = get_function_name(rule_str)
            exec(rule_str, {}, globals())
            self.g_rule = globals()[fun_name]
        # return pyo.Constraint(rule=self.g_rule)