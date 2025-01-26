import math


def round_to_n(x: float, n_digits: int) -> float:
    """Round a floating point to n significant digits

    Args:
        x (float): Number to round
        n_digits (int): Number of digits to keep

    Returns:
        float: Rounded version of x with n_digits digits
    """
    if not math.isfinite(x) or x == 0:
        return x
    main_digit = math.floor(math.log10(abs(x)))
    return round(x, -main_digit + n_digits - 1)
