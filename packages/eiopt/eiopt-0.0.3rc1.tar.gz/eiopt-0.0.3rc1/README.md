
# [eiopt](http://www.eiopt.com/)

eiopt is a simple and easy to use optimizer that allows the direct use of functions for optimization, it can handle a variety of problems such as single objective, multi-objective, etc., compatible with common optimizers such as pyomo, gurobi, etc.

Eiopt是一个简单易用的优化器，允许直接使用函数进行优化，它可以处理单目标、多目标等各种问题，与常用的优化器如pyomo、gurobi等兼容。

[Learn more](http://www.eiopt.com/)

## 单目标问题, Single objective problem

$$
\begin{aligned}
{Minimize\ } & f_1(x,y) = x+y^2, \\
{subject\ to\ } & x \geq 5, \\
& 2y \geq 4.
\end{aligned}
$$


```python
from eiopt import Model, Variable, Objective, Constraint

model = Model()
model.x = Variable()
model.y = Variable()
model.obj = Objective(lambda model: model.x +  model.y ** 2)
model.con = Constraint(lambda model: model.x>=5)
model.con = Constraint(lambda model: 2*model.y>=4)
result = model.solve()
print(result)
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


## 多目标问题, Multi-objective problem


# BNH 函数
[URL](https://pymoo.org/problems/multi/bnh.html)

$$
\begin{aligned}
{Minimize\ } & f_1(x) = 4x_1^2 + 4x_2^2, \\
{Minimize\ } & f_2(x) = (x_1-5)^2 + (x_2-5)^2,    \\
{subject\ to\ } & C_1(x) = (x_1-5)^2 + x_2^2 \leq 25, \\
& C_2(x) = (x_1-8)^2 + (x_2+3)^2 \geq 7.7, \\
& 0 \leq x_1 \leq 5, \\
& 0 \leq x_2 \leq 3.
\end{aligned}
$$

```python
from eiopt import *
model = Model()
model.x = Variable(2, lb=[0,0], ub=[5,3])
model.obj1 = Objective(lambda model:  4*model.x[0]**2 + 4*model.x[1]**2)
model.obj2 = Objective(lambda model: (model.x[0]-5)**2 + (model.x[1]-5)**2)
model.g1 = Constraint(lambda model: (model.x[0]-5)**2 + model.x[1]**2 <= 25)
model.g2 = Constraint(lambda model: (model.x[0]-8)**2 + (model.x[1]+3)**2 >= 7.7)
result = model.solve()
print(result)
```