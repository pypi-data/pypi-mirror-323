import numpy as np

maximize = -1
minimize = 1
INF = np.inf


pyomo_map = {
    "variable":"Var",
    "Model":"ConcreteModel",    
}



class Register(object):

    def __init__(self):
        self.module_dict = dict()

    def register_module(self):
        def _register(target):
            name = target.__name__.lower()
            self.module_dict[name] = target
            return target

        return _register

    def modules(self):
        return dict(self.module_dict)


VARIABLES = Register()


vtype_map = {
    "C":"Continuous",
    "c":"Continuous",
    "i":"Integer",    
    "I":"Integer",    
}


def is_single_level_tuple(obj):
    if isinstance(obj, tuple):
        return all(np.isscalar(elem) for elem in obj)
    return False

