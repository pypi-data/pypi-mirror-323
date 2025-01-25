from .common import *
from .variables import VariableBase, Variable
from .objective import Objective
from .constraint import Constraint
import pyomo.environ as pyo
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from .algorithms.ga import GA

class MoProblem(Problem):
    def __init__(self,
                 n_var,
                 n_obj,
                 n_constr,
                 xl,
                 xu, 
                 vtype,
                 model):
        super().__init__(n_var=n_var, 
                         n_obj=n_obj, 
                         n_constr=n_constr, 
                         xl=xl, 
                         xu=xu,
                         vtype=vtype)
        self.model = model


    def _evaluate(self, x, out):
        obj_list = []
        var = self.model.variables[0]
        # cal obj
        for v in x:
            var.set_value(v)
            obj_list.append([obj() * obj.sense for obj in self.model.objectives])
        out["F"] = np.array(obj_list)
        # cal ieq_constraints
        G_list = []
        for v in x:
            var.set_value(v)
            G_list.append([constr.g_rule(self.model) for constr in self.model.ieq_constraints])
        out["G"] = np.array(G_list)
        # cal eq_constraints
        H_list = []
        for v in x:
            self.model.variables[0].set_value(v)
            H_list.append([constr.h_rule() for constr in self.model.eq_constraints])
        out["H"] = np.array(H_list)
        return out



class Model:
    def __init__(self, name: str = ""):
        self.name = name
        self.variables = []
        self.objectives = []
        self.constraints = []
        self.eq_constraints = []
        self.ieq_constraints = []
        self.result = {"status":1,
                       "objetives":[],
                       "variables":[],
                       "constraints":[]}


    def __setattr__(self, name, value):
        if isinstance(value, VariableBase):
            if value.name != name:
                value.name = name
            self.variables.append(value)
        if isinstance(value, Objective):
            value.model = self
            self.objectives.append(value)
        if isinstance(value, Constraint):
            value.model = self
            if value.ctype:
                self.ieq_constraints.append(value)
            else:
                self.eq_constraints.append(value)
            self.constraints.append(value)
        self.__dict__[name] = value

    def addVariable(self, *args, **kwargs):
        if kwargs.get("name"):
            name = kwargs.get("name")
            if hasattr(self, name):
                raise ValueError(f"The name of varibale {name} already in the model\nyou can change it by:\nmodel.{name} = Variable()")
        else:
            raise ValueError(f"""Please input name of variable, like:
model.addVariable(name="x")
or
model.addVariable(name="x", vtype="C")
                             """)
        var = Variable(*args, **kwargs)
        self.variables.append(var)
        self.__dict__[name] = var
        return var
    
    def addObjective(self, *args, **kwargs):
        kwargs['model'] = kwargs.get("model", self)
        obj = Objective(*args, **kwargs)
        self.objectives.append(obj)
        return obj

    def addConstraint(self, *args, **kwargs):
        kwargs['model'] = kwargs.get("model", self)
        con = Constraint(*args, **kwargs)
        self.constraints.append(con)
        if con.ctype:
            self.ieq_constraints.append(con)
        else:
            self.eq_constraints.append(con)
        return con

    def to_pyomo(self):
        return pyo.ConcreteModel()
    
    def to_pyomo_str(self):
        if len(self.objectives) > 1:
            raise ValueError(f"Please input only 1 objective")

        self._pyomo_code = ["import pyomo.environ as pyo",
                            "model = pyo.ConcreteModel()"]
        for var in self.variables:
            self._pyomo_code.append(var.to_pyomo())
        for obj in self.objectives:
            self._pyomo_code.append(obj.to_pyomo())
        for con in self.variables:
            self._pyomo_code.append(con.to_pyomo())
        return "\n".join(self._pyomo_code)



    def solve_by_lp(self, solver="gurobi"):
        model = self.to_pyomo()
        for i, var in enumerate(self.variables):
            name = var.name if var.name else f"var{i}"
            setattr(model, name, var.to_pyomo())
        for j, obj in enumerate(self.objectives):
            setattr(model, f"obj_{j}", obj.to_pyomo())
        for j, con in enumerate(self.constraints):
            setattr(model, f"con_{j}", con.to_pyomo())
        solver = pyo.SolverFactory(solver)
        self.model = model
        solver.solve(model)
        self.result = solver._soln['solution']
        return self.result
    

    def solve_by_EA(self, solver="GA", *args, **kwargs):
        return globals()[solver](model=self, *args, **kwargs).solve()


    def solve(self, solver=None, *args, **kwargs):
        if len(self.objectives) <= 1:
            if solver is None:
                solver = "gurobi"
            if solver in ['cbc', 'gurobi', 'glpk', 'copt', 'cplex', "ipopt"]:
                results = self.solve_by_lp(solver=solver)
            else:
                results = self.solve_by_EA(solver=solver, *args, **kwargs)
                self.result = results
        else:
            problem = self.to_moo()
            if solver is None:
                solver = "NSGA2"
            algorithm = globals()[solver](pop_size=100)
            results = minimize(problem,
                        algorithm,
                        ('n_gen', 200),
                        seed=1,
                        verbose=True)
            self.result = results.__dict__
        return self.result

    def pprint(self):
        self.model.pprint()

    def to_moo(self):
        if len(self.variables) < 1:
            raise ValueError(f"You must define one variable, like:\n model.addVariable('C', name='x')")
        var = self.variables[0]
        for con in self.constraints:
            con.to_pymoo()
        n_var = var.shape[0]
        return MoProblem(n_var = n_var,
                n_obj = len(self.objectives),
                n_constr = len(self.constraints),
                xl = -999999 if var.lb == -np.inf else var.lb,
                xu = 999999 if var.ub == np.inf else var.ub,
                model = self,
                vtype=float,
                )

