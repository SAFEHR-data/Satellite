import re

# from: https://tinyurl.com/yfv7m927
_camel_case_pattern = re.compile(r"(?<!^)(?=[A-Z])")


def camel_to_snake_case(string: str) -> str:
    return _camel_case_pattern.sub("_", string).lower()
