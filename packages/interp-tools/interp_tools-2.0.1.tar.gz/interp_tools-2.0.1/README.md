use ```pip install interp-tools```

Python module for interpolating functions from one, two or three variables.

Examples of using the module:

Examle 1 for 1D interpolation
python: 
```import interp_tools
import numpy as np

function_dots = np.array([0, 1, 2, 3, 4, 5])

interpolator = interp_tools.Interp(
    function_dots, 1, np.array([1])
)

for i in range(8):
    print(f"x = {i / 5}, interp val = {interpolator.get_value(i / 5)}, real func val = {i / 5}")
```
```
# x = 0.0, interp val = 0.0, real func val = 0.0
# x = 0.2, interp val = 0.19999999999999998, real func val = 0.2
# x = 0.4, interp val = 0.39999999999999997, real func val = 0.4
# x = 0.6, interp val = 0.5999999999999999, real func val = 0.6
# x = 0.8, interp val = 0.7999999999999999, real func val = 0.8
# x = 1.0, interp val = 1.0, real func val = 1.0
# x = 1.2, interp val = 1.2, real func val = 1.2
# x = 1.4, interp val = 1.4, real func val = 1.4
```

Examle 2 for 1D interpolation
python:
```
import interp_tools
import numpy as np

function_dots = np.zeros(100)
for x in range(100):
    function_dots[x] = (x / 10) ** 2

interpolator = interp_tools.Interp(
    function_dots, 1, np.array([0.1])
)

for i in range(5):
    print(f"x = {i / 5}, interp val = {interpolator.get_value(i / 5)}, real func val = {((i / 5) ** 2) }")
```
```
# x = 0.0, interp val = 0.0, real func val = 0.0
# x = 0.2, interp val = 0.04000000000000001, real func val = 0.04000000000000001
# x = 0.4, interp val = 0.16000000000000003, real func val = 0.16000000000000003
# x = 0.6, interp val = 0.35999999999999993, real func val = 0.36
# x = 0.8, interp val = 0.6400000000000001, real func val = 0.6400000000000001
```


Example for 2D interpolation
python:
```
import interp_tools
import numpy as np

function_dots = np.zeros([100, 100])
for x in range(100):
    for y in range(100):
        function_dots[x, y] = x * y / 100

interpolator = interp_tools.Interp(
    function_dots, 2, np.array([0.1, 0.1])
)

for x in range(1, 4):
    for y in range(1, 4):
        print(f"x = {x / 5}, y = {y / 5}, interp val = {interpolator.get_value(x / 5, y / 5)}, real func val = {((x / 5) * (y / 5)) }")
```

```
#x = 0.2, y = 0.2, interp val = 0.04, real func val = 0.04000000000000001
# x = 0.2, y = 0.4, interp val = 0.08, real func val = 0.08000000000000002
# x = 0.2, y = 0.6, interp val = 0.11999999999999998, real func val = 0.12
# x = 0.4, y = 0.2, interp val = 0.08, real func val = 0.08000000000000002
# x = 0.4, y = 0.4, interp val = 0.16, real func val = 0.16000000000000003
# x = 0.4, y = 0.6, interp val = 0.23999999999999996, real func val = 0.24
# x = 0.6, y = 0.2, interp val = 0.11999999999999998, real func val = 0.12
# x = 0.6, y = 0.4, interp val = 0.23999999999999996, real func val = 0.24
# x = 0.6, y = 0.6, interp val = 0.34999999999999987, real func val = 0.36
```

Example of 3D interpolation
python:
import interp_tools
import numpy as np
```
function_dots = np.zeros([100, 100, 100])
for x in range(100):
    for y in range(100):
        for z in range(100):
            function_dots[x, y, z] = (x * y / 100 + z / 10)

interpolator = interp_tools.Interp(
    function_dots, 3, np.array([0.1, 0.1, 0.1])
)

for x in range(1, 4):
    for y in range(1, 4):
        for z in range(1, 4):
            print(f"x = {x / 5}, y = {y / 5}, z = {z / 5}, interp val = {interpolator.get_value(x / 5, y / 5, z / 5)}, real func val = {((x / 5) * (y / 5) + z / 5) }")
```


```
#x = 0.2, y = 0.2, z = 0.2, interp val = 0.24000000000000002, real func val = 0.24000000000000002
# x = 0.2, y = 0.2, z = 0.4, interp val = 0.44, real func val = 0.44000000000000006
# x = 0.2, y = 0.2, z = 0.6, interp val = 0.6399999999999999, real func val = 0.64
# x = 0.2, y = 0.4, z = 0.2, interp val = 0.28, real func val = 0.28
# x = 0.2, y = 0.4, z = 0.4, interp val = 0.48000000000000004, real func val = 0.48000000000000004
# x = 0.2, y = 0.4, z = 0.6, interp val = 0.6799999999999998, real func val = 0.6799999999999999
# x = 0.2, y = 0.6, z = 0.2, interp val = 0.32, real func val = 0.32
# x = 0.2, y = 0.6, z = 0.4, interp val = 0.52, real func val = 0.52
# x = 0.2, y = 0.6, z = 0.6, interp val = 0.7199999999999999, real func val = 0.72
# x = 0.4, y = 0.2, z = 0.2, interp val = 0.28, real func val = 0.28
# x = 0.4, y = 0.2, z = 0.4, interp val = 0.48000000000000004, real func val = 0.48000000000000004
# x = 0.4, y = 0.2, z = 0.6, interp val = 0.6799999999999998, real func val = 0.6799999999999999
# x = 0.4, y = 0.4, z = 0.2, interp val = 0.36, real func val = 0.36000000000000004
# x = 0.4, y = 0.4, z = 0.4, interp val = 0.56, real func val = 0.56
# x = 0.4, y = 0.4, z = 0.6, interp val = 0.7599999999999999, real func val = 0.76
# x = 0.4, y = 0.6, z = 0.2, interp val = 0.43999999999999995, real func val = 0.44
# x = 0.4, y = 0.6, z = 0.4, interp val = 0.64, real func val = 0.64
# x = 0.4, y = 0.6, z = 0.6, interp val = 0.84, real func val = 0.84
# x = 0.6, y = 0.2, z = 0.2, interp val = 0.32, real func val = 0.32
# x = 0.6, y = 0.2, z = 0.4, interp val = 0.52, real func val = 0.52
# x = 0.6, y = 0.2, z = 0.6, interp val = 0.7199999999999999, real func val = 0.72
# x = 0.6, y = 0.4, z = 0.2, interp val = 0.43999999999999995, real func val = 0.44
# x = 0.6, y = 0.4, z = 0.4, interp val = 0.64, real func val = 0.64
# x = 0.6, y = 0.4, z = 0.6, interp val = 0.84, real func val = 0.84
# x = 0.6, y = 0.6, z = 0.2, interp val = 0.5499999999999999, real func val = 0.56
# x = 0.6, y = 0.6, z = 0.4, interp val = 0.7499999999999998, real func val = 0.76
# x = 0.6, y = 0.6, z = 0.6, interp val = 0.95, real func val = 0.96
```
