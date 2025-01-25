
# eiopt

This simple project is an example of a rainpy project build.

[Learn more](https://github.com/zmdsn/rainpy)


```python
from eiopt import Model, Variable, Objective, Constraint

model = Model()
model.x = Variable()
model.y = Variable()
model.obj = Objective(lambda model: model.x +  model.y ** 2)
model.con = Constraint(lambda model: model.x>=5)
model.con = Constraint(lambda model: 2*model.y>=4)
result = model.solve()
```

result format:
```json
{
    'status': 'optimal', 
    'message': 'Model was solved to optimality (subject to tolerances), and an optimal solution is available.', 
    'objective': 9.0, 
    'gap': 0.0, 
    'var': {
        'x2': 5.0, 
        'x3': 2.0
    }
}
```