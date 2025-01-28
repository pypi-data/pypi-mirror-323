import matrix_operations_cuni

A = matrix_operations_cuni.Matrix([[1,2,3], [2,2,2], [9,8,0]])
B = matrix_operations_cuni.Matrix([[9,9,8], [7,0,0], [2,3,12]])

multiply = matrix_operations_cuni.mat_mul(A,B) # mat_mul(matrix1, matrix2)x;
multiply_reverse = matrix_operations_cuni.mat_mul(B,A)

add = matrix_operations_cuni.add(A,B)
sub = matrix_operations_cuni.sub(A,B)
mul_scalar = matrix_operations_cuni.mul_scalar(A, 8)

multiply.pretty_print()
print()
multiply_reverse.pretty_print()
print()
add.pretty_print()
print()
sub.pretty_print()
print()
mul_scalar.pretty_print()

