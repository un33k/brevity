import os


def serializer_class(serializer_class):
    def decorator(func):
        func.serializer_class = serializer_class
        return func
    return decorator
