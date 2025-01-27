from matrix_operations_cuni.core import Matrix


def valid_for_sum(matrix1: Matrix, matrix2: Matrix):
    """
    Checks whether you can add 2 matrices together.
    :param matrix1: First matrix to add.
    :param matrix2: Second matrix to add.
    :return: True/False based on whether it is possible.
    """
    if (matrix1.cols == matrix2.cols) and (matrix1.rows == matrix2.rows):
        return True
    return False


def valid_for_mul(matrix1: Matrix, matrix2: Matrix):
    """
    Checks whether you can multiply 2 matrices together.
    :param matrix1: First matrix to multiply.
    :param matrix2: Second matrix to multiply.
    :return: True/False based on whether it is possible.
    """
    if matrix1.cols == matrix2.rows:
        return True
    return False


def add(matrix1: Matrix, matrix2: Matrix) -> Matrix:
    """
    Performs addition on 2 matrices.
    :param matrix1: First matrix to add.
    :param matrix2: Second matrix to add.
    :return: Sum of 2 matrices.
    """
    if not valid_for_sum(matrix1, matrix2):
        raise ValueError("Incorrect dimensions for matrices. These cannot be added.")
    result = []
    for r_index in range(matrix1.rows):
        row = []
        for c_index in range(matrix1.cols):
            row.append(matrix1[r_index, c_index] + matrix2[r_index, c_index])
        result.append(row)
    return Matrix(result)


def mul_scalar(matrix: Matrix, scalar: (int, float)) -> Matrix:
    """
    Performs multiplication of a matrix by a scalar.
    :param matrix: Matrix to multiply.
    :param scalar: Scalar that multiplies the matrix.
    :return: Matrix multipied by scalar.
    """
    result = []
    for r_index in range(matrix.rows):
        row = []
        for c_index in range(matrix.cols):
            row.append(matrix[r_index, c_index] * scalar)
        result.append(row)
    return Matrix(result)


def sub(matrix1: Matrix, matrix2: Matrix) -> Matrix:
    """
    Subtracts 2 matrices by multiplying the 2nd by -1 and then
    adding it to the first one.
    :param matrix1: Matrix to subtract from.
    :param matrix2: Matrix to subtract.
    :return: Result of subtraction.
    """
    return add(matrix1, mul_scalar(matrix2, -1))


def mat_mul(matrix1: Matrix, matrix2: Matrix) -> Matrix:
    """
    Performs multiplication of 2 matrices.
    :param matrix1: First matrix to add.
    :param matrix2: Second matrix to add.
    :return: Product of 2 matrices.
    """
    if not valid_for_mul(matrix1, matrix2):
        raise ValueError(
            "Incorrect dimensions for matrices. These cannot be multiplied."
        )
    result = []
    for r_index in range(matrix1.rows):
        row = []
        for c_index in range(matrix2.cols):
            temp = 0    # result for one element
            for k_index in range(matrix2.rows):  # matrix1.cols == matrix2.rows
                temp += matrix1[r_index, k_index] * matrix2[k_index, c_index]
            row.append(temp)
        result.append(row)
    return Matrix(result)

if __name__ == "__main__":
    matica1 = Matrix([[1, 2, 3], [4, 5, 6]])
    matica2 = Matrix([[1, 2], [9, 1], [1, 3]])
    print(mat_mul(matica1, matica2))
