import pytest
from matrix_operations_cuni.core import Matrix


def test__validate_matrix():
    valid_matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert Matrix._validate_matrix(valid_matrix) is True

    valid_matrix = [[1, 2.6, 3], [4.8, 5, 6], [7, 8.9, 9]]
    assert Matrix._validate_matrix(valid_matrix) is True

    invalid_matrix = [[1, 2], [3, 4, 5]]
    assert Matrix._validate_matrix(invalid_matrix) is False

    invalid_matrix = [[1, 2, "x"], [3, 4, 5]]
    assert Matrix._validate_matrix(invalid_matrix) is False

    invalid_matrix = [[1, "x"], [3, 4, 5]]
    assert Matrix._validate_matrix(invalid_matrix) is False


def test_getitem():
    matrix = Matrix([[1, 2], [3, 4]])
    assert matrix[0, 0] == 1
    assert matrix[1, 1] == 4
    assert matrix[0] == [1, 2]
    with pytest.raises(IndexError):
        _ = matrix[2, 2]
    with pytest.raises(TypeError):
        _ = matrix["invalid"]

