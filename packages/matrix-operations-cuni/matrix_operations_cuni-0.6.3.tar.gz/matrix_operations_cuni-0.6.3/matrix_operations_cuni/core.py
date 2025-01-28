class Matrix:
    def __init__(self, data):
        if not self._validate_matrix(data):
            raise ValueError(
                "Invalid matrix data. All rows should be the same size and consist of numbers."
            )
        self.data = data
        self.rows = len(data)
        self.cols = len(data[0])

    @staticmethod
    def _validate_matrix(matrix):
        """
        Validates whether the input follows the matrix structure.
        :param matrix: A nested list of lists.
        :return: True/False based on whether it is a valid representation of a matrix.
        """
        if (
            not isinstance(matrix, list)
            or not all(isinstance(row, list) for row in matrix)
            or not all(
                isinstance(element, (int, float)) for row in matrix for element in row
            )
        ):
            return False
        if (len(matrix) == 0) or (len(set(len(row) for row in matrix)) > 1):
            return False
        return True

    def __repr__(self):
        return str(self.data)

    def __getitem__(self, item: int or tuple):
        """
        Enables to access individual elements of a matrix.
        Return a row by supplying an integer.
        Return an element of a matrix by supplying a tuple
        :param item: which element to return
        :return: chosen element
        """
        if (isinstance(item, tuple)) and (len(item) == 2):
            r_index, c_index = item
            if (0 <= r_index < self.rows) and (0 <= c_index < self.cols):
                return self.data[r_index][c_index]
            raise IndexError("Matrix index out of range")
        elif isinstance(item, int):
            if 0 <= item < self.rows:
                return self.data[item]
            raise IndexError("Matrix index out of range")
        raise TypeError("Matrix indices must be integers or tuples of integers")

    def pretty_print(self):
        """
        Prints the matrix in a simple, readable format.
        Handles -0.0 by converting it to 0.0.
        """
        for r_index in range(self.rows):
            row_values = []
            for c_index in range(self.cols):
                value = self[r_index, c_index]
                if int(value) == value: # fixes -0.0, 2.0, etc.
                    value = int(value)
                if isinstance(value, float):
                    formatted = f"{value:8.4f}" # 4 decimals, 8 chars width
                else:
                    formatted = f"{value:8}"
                row_values.append(formatted)
            print("\t".join(row_values))


if __name__ == "__main__":
    testMatica = Matrix([[1, 2, 3], [3, 3, 4]])
    print(testMatica)
    print(testMatica.rows)
    testMatica.pretty_print()
