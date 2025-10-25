def choose_default(values: list[str], possible_names: set[str]):
    for val in values:
        if val.lower() in possible_names:
            return val
    return "empty"