# mpspy

A simple implementation to read MPS files containing the definitions
of mixed-integer programs such as found in
[MIPLIB](https://miplib.zib.de/index.html).

## Usage:

```python
import mpspy

# Read instance
instance = mpspy.read_mps('instance.mps')

# Access instance

print(instance.var_lb)
print(instance.var_ub)
print(instance.coeffs)

```

Note: This implementation is designed to read MIPLIB instances only.
