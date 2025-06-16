"""
Example Semantic Kernel plugin demonstrating basic implementation patterns.

This module provides a simple calculator plugin that showcases:
- Proper function decoration with @kernel_function
- Type hints using modern Python syntax
- Input validation and error handling
- Comprehensive docstrings
- Return value descriptions
"""

from typing import Annotated
from semantic_kernel.functions import kernel_function


class CalculatorPlugin:
    """
    A simple calculator plugin demonstrating Semantic Kernel function patterns.
    
    This plugin provides basic mathematical operations and serves as a template
    for implementing other tools in the multi-agent system.
    """

    @kernel_function(
        name="add_numbers",
        description="Add two numbers together and return the result"
    )
    def add_numbers(
        self,
        first_number: Annotated[float, "The first number to add"],
        second_number: Annotated[float, "The second number to add"]
    ) -> Annotated[float, "The sum of the two numbers"]:
        """
        Add two numbers together.
        
        Args:
            first_number: The first number to add
            second_number: The second number to add
            
        Returns:
            The sum of the two numbers
            
        Example:
            >>> plugin = ExampleCalculatorPlugin()
            >>> result = plugin.add_numbers(5.0, 3.0)
            >>> print(result)
            8.0
        """
        return first_number + second_number

    @kernel_function(
        name="subtract_numbers",
        description="Subtract the second number from the first and return the result"
    )
    def subtract_numbers(
        self,
        minuend: Annotated[float, "The number to subtract from"],
        subtrahend: Annotated[float, "The number to subtract"]
    ) -> Annotated[float, "The difference between the two numbers"]:
        """
        Subtract the second number from the first.
        
        Args:
            minuend: The number to subtract from
            subtrahend: The number to subtract
            
        Returns:
            The difference between the two numbers
            
        Example:
            >>> plugin = ExampleCalculatorPlugin()
            >>> result = plugin.subtract_numbers(10.0, 4.0)
            >>> print(result)
            6.0
        """
        return minuend - subtrahend

    @kernel_function(
        name="multiply_numbers",
        description="Multiply two numbers together and return the result"
    )
    def multiply_numbers(
        self,
        first_number: Annotated[float, "The first number to multiply"],
        second_number: Annotated[float, "The second number to multiply"]
    ) -> Annotated[float, "The product of the two numbers"]:
        """
        Multiply two numbers together.
        
        Args:
            first_number: The first number to multiply
            second_number: The second number to multiply
            
        Returns:
            The product of the two numbers
            
        Example:
            >>> plugin = ExampleCalculatorPlugin()
            >>> result = plugin.multiply_numbers(4.0, 6.0)
            >>> print(result)
            24.0
        """
        return first_number * second_number

    @kernel_function(
        name="divide_numbers",
        description="Divide the first number by the second number and return the result"
    )
    def divide_numbers(
        self,
        dividend: Annotated[float, "The number to be divided"],
        divisor: Annotated[float, "The number to divide by (cannot be zero)"]
    ) -> Annotated[float, "The quotient of the division"]:
        """
        Divide the first number by the second number.
        
        Args:
            dividend: The number to be divided
            divisor: The number to divide by (cannot be zero)
            
        Returns:
            The quotient of the division
            
        Raises:
            ValueError: If divisor is zero
            
        Example:
            >>> plugin = ExampleCalculatorPlugin()
            >>> result = plugin.divide_numbers(10.0, 2.0)
            >>> print(result)
            5.0
        """
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        return dividend / divisor

    @kernel_function(
        name="calculate_percentage",
        description="Calculate what percentage the part represents of the whole"
    )
    def calculate_percentage(
        self,
        part: Annotated[float, "The part value"],
        whole: Annotated[float, "The whole value (cannot be zero)"]
    ) -> Annotated[float, "The percentage value (0-100)"]:
        """
        Calculate what percentage the part represents of the whole.
        
        Args:
            part: The part value
            whole: The whole value (cannot be zero)
            
        Returns:
            The percentage value (0-100)
            
        Raises:
            ValueError: If whole is zero
            
        Example:
            >>> plugin = ExampleCalculatorPlugin()
            >>> result = plugin.calculate_percentage(25.0, 100.0)
            >>> print(result)
            25.0
        """
        if whole == 0:
            raise ValueError("Cannot calculate percentage with zero as whole")
        return (part / whole) * 100.0

    @kernel_function(
        name="format_currency",
        description="Format a number as currency with proper decimal places"
    )
    def format_currency(
        self,
        amount: Annotated[float, "The amount to format"],
        currency_symbol: Annotated[str, "The currency symbol to use"] = "$"
    ) -> Annotated[str, "The formatted currency string"]:
        """
        Format a number as currency with proper decimal places.
        
        Args:
            amount: The amount to format
            currency_symbol: The currency symbol to use (defaults to "$")
            
        Returns:
            The formatted currency string
            
        Example:
            >>> plugin = ExampleCalculatorPlugin()
            >>> result = plugin.format_currency(123.456)
            >>> print(result)
            $123.46
        """
        return f"{currency_symbol}{amount:.2f}"