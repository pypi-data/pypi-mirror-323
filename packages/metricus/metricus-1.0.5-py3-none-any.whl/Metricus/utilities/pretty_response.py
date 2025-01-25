from typing import Union

class PrettyResponse:
  """
  The PrettyResponse class provides static methods to generate formatted strings
  for presenting conversion results in a user-friendly and readable manner.
  """

  @staticmethod
  def simple_string(value: float, from_unit: str, to_unit: str, result: Union[str, float], rounded_result: bool) -> str:
    """
    Generates a formatted string for a simple conversion from one unit to another.

    Parameters:
    - value (float): The numeric value to be converted.
    - from_unit (str): The unit of the input value.
    - to_unit (str): The target unit to which the value is converted.
    - result (Union[str, float]): The conversion result, which can be numeric or string representation.
    - rounded_result (bool): Indicates whether the result is rounded.

    Returns:
    - str: A descriptive string summarizing the conversion.

    Example:
    >>> response = PrettyResponse.simple_string(100, "meters", "feet", 328.084, True)
    >>> print(response)
    "The conversion of 100 meters to feet equals 328.084. This value is rounded."
    """
    simple_string = (
      f"The conversion of {value} {from_unit} to {to_unit} equals {result}. "
      f"This value is {'rounded' if rounded_result else 'not rounded'}."
    )
    return simple_string

  @staticmethod
  def complex_string(first_value: float, first_unit: str, second_value: float, second_unit: str, result: Union[str, float], rounded_result: bool) -> str:
    """
    Generates a formatted string for conversions involving two input values and units.

    Parameters:
    - first_value (float): The first numeric value in the conversion process.
    - first_unit (str): The unit of the first input value.
    - second_value (float): The second numeric value in the conversion process.
    - second_unit (str): The unit of the second input value.
    - result (Union[str, float]): The conversion result, which can be numeric or string representation.
    - rounded_result (bool): Indicates whether the result is rounded.

    Returns:
    - str: A descriptive string summarizing the conversion.

    Example:
    >>> response = PrettyResponse.complex_string(50, "kilograms", 100, "grams", 0.5, False)
    >>> print(response)
    "The conversion of 50 kilograms in 100 grams equals 0.5. The result is not rounded."
    """
    complex_string = (
      f"The conversion of {first_value} {first_unit} in {second_value} {second_unit} "
      f"equals {result}. The result is {'rounded' if rounded_result else 'not rounded'}."
    )
    return complex_string
