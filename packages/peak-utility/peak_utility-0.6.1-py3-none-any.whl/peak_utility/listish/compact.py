def compact(listish: list | tuple | dict):
    """Removes all none values from a list, tuple, or dictionary"""
    if isinstance(listish, dict):
        return {k: v for k, v in listish.items() if v is not None}
    return [item for item in listish if item is not None]
