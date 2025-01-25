import pytest
from matrix_operations_cuni.transformations import Transformations


def test_transpose():
    matrix = Transformations([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    transposed = matrix.transpose()
    expected = Transformations([[1, 4, 7], [2, 5, 8], [3, 6, 9]])
    assert transposed.data == expected.data

    matrix = Transformations([[1]])
    transposed = matrix.transpose()
    expected = Transformations([[1]])
    assert transposed.data == expected.data


def test_rref():
    matrix = Transformations([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    rref_form = matrix.rref()
    correct_rref = Transformations([[1, 0, -1], [0, 1, 2], [0, 0, 0]])
    assert rref_form.data == correct_rref.data

    matrix = Transformations([[1, 2, 0], [0, 5, 6], [7, 0, 9]])
    rref_form = matrix.rref()
    correct_rref = Transformations([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    assert rref_form.data == correct_rref.data

    matrix = Transformations([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    rref_form = matrix.rref()
    correct_rref = Transformations([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
    assert rref_form.data == correct_rref.data

    matrix = Transformations([[1, 0.25, 8], [2, 2, 0], [0, 0, 0]])
    rref_form = matrix.rref()
    rounded_rref = []
    for row in rref_form.data:
        rounded_row = []
        for val in row:
            rounded_row.append(round(val, 2))
        rounded_rref.append(rounded_row)
    correct_rref = Transformations([[1, 0, 10.67], [0, 1, -10.67], [0, 0, 0]])
    assert rounded_rref == correct_rref.data


def test_inverse():
    matrix = Transformations([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    inverse = matrix.inverse()
    correct_inverse = Transformations([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
    assert inverse.data == correct_inverse.data

    matrix = Transformations([[1]])
    inverse = matrix.inverse()
    correct_inverse = Transformations([[1]])
    assert inverse.data == correct_inverse.data

    matrix = Transformations([[2, 2, 3], [1, 3, 4], [1, 1, 1]])
    inverse = matrix.inverse()
    correct_inverse = Transformations(
        [[0.5, -0.5, 0.5], [-1.5, 0.5, 2.5], [1.0, -0.0, -2.0]]
    )
    assert inverse.data == correct_inverse.data

    with pytest.raises(ValueError):
        matrix = Transformations([[2, 2, 3], [1, 3, 4]])
        matrix.inverse()

    with pytest.raises(ValueError):
        matrix = Transformations([[2, 2, 3], [1, 3, 4], [0, 0, 0]])
        matrix.inverse()

    with pytest.raises(ValueError):
        matrix = Transformations([[0]])
        matrix.inverse()


def test_trace():
    matrix = Transformations([[90, 2, 90], [1, 1, 0], [34, 11, 1]])
    trace = matrix.trace()
    correct_trace = 92
    assert trace == correct_trace

    with pytest.raises(ValueError):
        matrix = Transformations([[2, 2, 3], [1, 3, 4]])
        matrix.trace()
