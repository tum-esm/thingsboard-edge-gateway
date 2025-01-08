def avg_list(input_list: list[float], round_digits: int = 2) -> float:
    """Averages a list of float.
    Returns a float rounded to defined digits."""
    return round(sum(input_list) / len(input_list), round_digits)
