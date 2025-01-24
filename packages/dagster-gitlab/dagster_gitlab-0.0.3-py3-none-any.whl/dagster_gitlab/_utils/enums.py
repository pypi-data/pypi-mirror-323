from enum import Enum


class ClientType(str, Enum):
    REST = " rest"
    GRAPHQL = " graphql"
