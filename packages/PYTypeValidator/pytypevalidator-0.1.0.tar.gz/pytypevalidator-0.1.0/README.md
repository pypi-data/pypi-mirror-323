# TypeValidator Class

## Overview

The `TypeValidator` class is a simple utility designed to validate the types of variables in Python. It provides methods to validate the type of a single value as well as multiple values against their expected types. This can be especially useful for ensuring data integrity and correctness in your code when dealing with dynamic data or user inputs.

## Features

- **Single value validation**: Validate if a single value matches the expected type.
- **Multiple value validation**: Validate a list of values against a list of expected types.
- **Error handling**: Raises an exception if the number of values does not match the number of expected types in batch validation.

## Methods

### `validate(self, value, expected_type)`

This method validates whether a single value matches the expected type.

**Parameters**:
- `value`: The value to check.
- `expected_type`: The type that the value is expected to be.

**Returns**:
- `True` if the value matches the expected type, otherwise `False`.

**Example Usage**:
```python
// Validate a single Variabale
type_validator = TypeValidator()
result = type_validator.validate(42, int)
print(result)  # Output: True

// Check multiple values
id  = 0
email = 1
isActiveAccount = False
Amount = 12.78

values = [id, email,isActiveAccount, Amount]
expected_types = [int, str,bool, float]
print(validator.validate_all(values, expected_types))# [True,False, True, True]