def exception_msg(exception: Exception) -> str:
    return f'{exception.__class__.__name__}: {exception}'
