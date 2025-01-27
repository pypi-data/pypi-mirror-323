from matrix_operations_cuni import Transformations

A = Transformations([[9,8,7,8], [1,1,1,10], [1,2,3,8], [0,0,1,1]])
trace = A.trace()
A.inverse().pretty_print()
print(f"Trace of A: {trace}")
print()

B = Transformations([[1,2,3,4,9,8], [9,9,9,1,1,1]])
B.rref().pretty_print()