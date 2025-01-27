"""
Custom exception classes for PyJolt
"""
from typing import Type

class DuplicateRoutePath(Exception):
    """
    Error for duplicate route path
    """

    def __init__(self, message):
        self.message = message

class DuplicateExceptionHandler(Exception):
    """
    Error for duplicate registered exception handler
    """
    def __init__(self, message):
        self.message = message

class Jinja2NotInitilized(Exception):
    """
    Error if jinja2 is not initilized
    """
    def __init__(self):
        self.message = "Jinja2 render engine is not initilized."

class MissingExtension(Exception):
    """
    Error for missinf extension
    """
    def __init__(self, ext_name: str):
        self.message = f"Extension with name {ext_name} not found on application."

class MissingDependencyInjectionMethod(Exception):
    """
    Error for missing dependency injection method.
    app._dependency_injection_map.get() returns None
    """
    def __init__(self, injectable: Type):
        self.message = f"Missing dependency injection method. Please provide a dependency injection method for the dependency: {injectable.__name__}"
