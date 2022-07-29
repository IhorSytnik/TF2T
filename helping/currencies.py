from classes.multiValueEnum import MultiValueEnum


class Currencies(MultiValueEnum):
    """
    Enum for item currency DefIndexes and ClassIds

    First value - DefIndex
    Second value - ClassId

    """
    SCRAP =     '5000', '2675'
    RECLAIMED = '5001', '5564'
    REFINED =   '5002', '2674'
    KEY =       '5021', '101785959'

    def get_def_index(self):
        return self._all_values[0]

    def get_class_id(self):
        return self._all_values[1]
