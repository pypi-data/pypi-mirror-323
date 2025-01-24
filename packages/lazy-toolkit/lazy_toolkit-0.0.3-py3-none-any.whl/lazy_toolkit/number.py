import math


def decimal_position(float_str: str | float) -> int | None:
    """Check the decimal position of a float number
    """
    if not isinstance(float_str, str):
        float_str = str(float_str)

    try:
        if float_str.isdigit():
            return 0
        decimal_part: str = float_str.split('.')[1].rstrip('0')
        return len(decimal_part)
    except BaseException:
        return None


def decimal_position_v2(float_str: str | float) -> int:
    return int(math.log(float(float_str), 0.1))


def digit_chunk(value: int, chunk: int) -> list[int]:
    """Split a value into chunks of a given size
    E.g.: digit_chunk(10, 3) -> [3, 3, 3, 1]
    """
    result: list[int] = list()
    while value > 0:
        if value >= chunk:
            result.append(chunk)
            value -= chunk
        else:
            result.append(value)
            value = 0
    return result


def num_to_pct(value: float | int) -> str:
    """Convert a number to percentage
    """
    return '%.2f%%' % (value * 100)
