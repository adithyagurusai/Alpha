from enum import Enum


class QueryMode(str, Enum):
    DETERMINISTIC = "deterministic"
    SEMANTIC = "semantic"
    AUTO = "auto"