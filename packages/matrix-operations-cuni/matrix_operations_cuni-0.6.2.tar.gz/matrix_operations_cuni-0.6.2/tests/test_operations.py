import pytest
from matrix_operations_cuni.operations import *
from matrix_operations_cuni.core import Matrix


def test_add():
    matrix_one = Matrix([[1, 2, 3], [4, 5, 6]])
    matrix_two = Matrix([[1, 2, 9], [1, 3, 8]])
    addition = add(matrix_one, matrix_two)
    correct_addition = Matrix([[2, 4, 12], [5, 8, 14]])
    assert addition.data == correct_addition.data

    with pytest.raises(ValueError):
        matrix_one = Matrix([[1, 2, 3], [4, 5, 6]])
        matrix_two = Matrix([[1, 2], [1, 3]])
        add(matrix_one, matrix_two)


def test_mul_scalar():
    matrix_one = Matrix([[1, 2, 3], [4, 5, 6]])
    scalar = 0.25
    scalar_mul = mul_scalar(matrix_one, scalar)
    correct_scalar_mul = Matrix([[0.25, 0.5, 0.75], [1, 1.25, 1.5]])
    assert scalar_mul.data == correct_scalar_mul.data


def test_sub():
    matrix_one = Matrix([[1, 2, 3], [4, 5, 6]])
    matrix_two = Matrix([[1, 2, 9], [1, 3, 8]])
    addition = sub(matrix_one, matrix_two)
    correct_addition = Matrix([[0, 0, -6], [3, 2, -2]])
    assert addition.data == correct_addition.data

    with pytest.raises(ValueError):
        matrix_one = Matrix([[1, 2, 3], [4, 5, 6]])
        matrix_two = Matrix([[1, 2], [1, 3]])
        sub(matrix_one, matrix_two)


def test_mat_mul():
    matrix_one = Matrix([[1, 2, 3], [4, 5, 6]])
    matrix_two = Matrix([[1, 2], [9, 1], [1, 3]])
    matrix_mul = mat_mul(matrix_one, matrix_two)
    correct_matrix_mul = Matrix([[22, 13], [55, 31]])
    assert matrix_mul.data == correct_matrix_mul.data

    with pytest.raises(ValueError):
        matrix_one = Matrix([[1, 2, 3], [4, 5, 6]])
        matrix_two = Matrix([[1, 2], [1, 3]])
        mat_mul(matrix_one, matrix_two)
