from enum import Enum


class MultiValueEnum(Enum):
    def __new__(cls, *args):
        obj = object.__new__(cls)
        # first value is canonical value
        obj._value_ = args[0]
        for other_value in args[1:]:
            cls._value2member_map_[other_value] = obj
        obj._all_values = args
        return obj

    def __repr__(self):
        return '<%s.%s: %s>' % (
                self.__class__.__name__,
                self._name_,
                ', '.join([repr(v) for v in self._all_values]),
                )
