import numpy as np
import scipy.linalg as alg

P = np.array([
    [0.8, 0.1, 0.1, 0], 
    [0.1, 0.5, 0.2, 0.2],
    [0.1, 0.3, 0.3, 0.3],
    [0, 0, 0, 1]])
P_inner = np.array([
    [0.8, 0.1, 0.1], 
    [0.1, 0.5, 0.2],
    [0.1, 0.3, 0.3]])
print("P matirx:")
print(P)
print("====================1(a)=====================")
# 1(a)
P_2_year = np.linalg.matrix_power(P, 2)
print(P_2_year)
print(np.sum(P_2_year, 1))
print("====================1(b)=====================")

# 1(b)
if (np.linalg.det(P) > 0 and np.linalg.det(P_inner) > 0):
    print("P is a postive definite matrix")
P_1_month = alg.fractional_matrix_power(P, 1/12)
print(np.sum(P_1_month, 1))
print(np.round(P_1_month, 2))
print("====================1(c)=====================")

# 1(c)
P_infinity = np.linalg.matrix_power(P, 10000)
print(P_infinity)
print("====================1(d)=====================")
# 1(d)
for i in range(100):
    P_infinity = np.linalg.matrix_power(P, i)
    print(np.round(P_infinity, 100))
