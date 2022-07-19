from typing import Tuple, Union


class OperationId:
    """Create and compare a tuple of numbers.

    Often added as an attribute to a gate which gives a number to
    that particular gate.

    Attributes:
        numbers (Tuple(int)): tuple of integers describing all the ids
            that a given operation has.
    """

    DEFAULT_NOT_INIT = -1

    def __init__(self, numbers_tuple: Union[Tuple[int, ...], int, None] = None):

        if numbers_tuple is None:
            numbers_tuple = (OperationId.DEFAULT_NOT_INIT,)

        if not isinstance(numbers_tuple, tuple):
            # cast to int
            x = int(numbers_tuple)
            numbers_tuple = (x,)

        self.numbers = tuple(numbers_tuple)

    def add_decomp_level(self) -> "OperationId":
        """Return an OperationID with the same numbers as self with 0 appended.

        Returns:
            OperationId: An OperationID with the same numbers as self with 0 appended.
        """
        return OperationId(self.numbers + (0,))

    def advance_decomp(self) -> "OperationId":
        """Return an OperationID with the same numbers as self with last number
            incremented by 1..

        Returns:
            OperationId: An OperationID with the same numbers as self ith last number
            incremented by 1.
        """
        last_number = self.numbers[-1]
        return OperationId(self.numbers[:-1] + (last_number + 1,))

    def _cmp_tuple(self) -> Tuple[int, ...]:
        return self.numbers

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, OperationId):
            return NotImplemented
        return self._cmp_tuple() == other._cmp_tuple()

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, OperationId):
            return NotImplemented
        return self._cmp_tuple() != other._cmp_tuple()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, OperationId):
            return NotImplemented
        return self._cmp_tuple() < other._cmp_tuple()

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, OperationId):
            return NotImplemented
        return self._cmp_tuple() > other._cmp_tuple()

    def __le__(self, other: object) -> bool:
        if not isinstance(other, OperationId):
            return NotImplemented
        return self._cmp_tuple() <= other._cmp_tuple()

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, OperationId):
            return NotImplemented
        return self._cmp_tuple() >= other._cmp_tuple()


LEFT_MOST_OP = OperationId((0,))
RIGHT_MOST_OP = OperationId((int(1e22),))
