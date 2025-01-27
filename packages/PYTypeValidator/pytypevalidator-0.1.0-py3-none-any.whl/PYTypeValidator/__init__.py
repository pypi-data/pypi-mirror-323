class TypeValidator:
    def __init__(self):
        pass

    def validate(self, value, expected_type):
        """
        Validate the type of a value.

        :param value: The value to check.
        :param expected_type: The type the value should be.
        :return: True if the value is of the expected type, otherwise False.
        """
        if isinstance(value, expected_type):
            return True
        else:
            return False

    def validate_all(self, values, expected_types):
        """
        Validate the types of multiple values.

        :param values: A list of values to check.
        :param expected_types: A list of expected types corresponding to each value.
        :return: A list of booleans indicating if the values match the expected types.
        """
        if len(values) != len(expected_types):
            raise ValueError("The number of values must match the number of expected types.")

        return [self.validate(value, expected_type) for value, expected_type in zip(values, expected_types)]



