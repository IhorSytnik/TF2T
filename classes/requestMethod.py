from enum import Enum


class RequestMethod(Enum):
    DELETE = 'delete'
    GET = 'get'
    HEAD = 'head'
    PATCH = 'patch'
    POST = 'post'
    PUT = 'put'