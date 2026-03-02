import re


def validate_flat_number(flat: str) -> bool:
    """
    Valid format:
    Lane: A-O
    House: 1-10
    Floor: G, F, S (Ground, First, Second)

    Example: A5S
    """

    pattern = r"^[A-O](10|[1-9])[GFS]$"
    return bool(re.match(pattern, flat))