from string import ascii_uppercase


def num_to_letters(num: int) -> str:
    """
    Convert a positive integer to its corresponding uppercase
    alphabetical representation.

    Parameters
    ----------
    num : int
        A positive integer to convert to an alphabetical
        representation. Must be greater than 0.

    Returns
    -------
    str
        The corresponding uppercase alphabetical representation of
        the given integer.

    Raises
    ------
    ValueError
        If the input `num` is less than or equal to 0, an exception
        is raised indicating an invalid input.

    Notes
    -----
    The mapping is consecutive, with 1 corresponding to 'A', 2 to 'B', ...,
    and 27 to 'AA'.
    """
    if num <= 0:
        raise ValueError("Sequence ID count must be greater than 0")
    result = ""
    while num > 0:
        num -= 1
        result = ascii_uppercase[num % 26] + result
        num //= 26
    return result


class IDRecord(object):
    """
    Manages a sequence ID record to automatically handle sequence IDs
    in the AlphaFold3 input file.

    Attributes
    ----------
    _seq_id : list of str or None
        The stored sequence IDs.
    _num : int or None
        The number of ligand sequences, default is 1.T his value
        will be overwritten if `seq_id` is specified.
    is_registered : bool
        A flag indicating whether the record is already registered or not.
    """
    def __init__(self, num: int = 1, seq_id: list[str] | None = None):
        self._seq_id: list[str] | None= seq_id
        if self._seq_id is None:
            self._num = num
        else:
            self._num = len(seq_id)
        self.is_registered: bool = False

    @property
    def num(self) -> int:
        return self._num

    def get_id(self) -> list[str]:
        return self._seq_id

    def set_id(self, seq_id: list[str]) -> None:
        self._seq_id = seq_id
        self._num = len(seq_id)

    def remove_id(self) -> None:
        self._seq_id = None
        self.is_registered = False


class IDRegister(object):
    """
    Manages the registration and generation of unique sequence IDs.

    This class ensures that sequence IDs are unique and allows for the
    registration of existing IDs as well as the generation of new, unique
    IDs based on an internal counter. It is primarily designed to prevent
    duplication and collisions of IDs in the AlphaFold3 input file.

    Attributes
    ----------
    _count : int
        The internal counter used for generating unique sequence IDs.
    _registered_ids : set
        A set that stores all the registered sequence IDs to ensure
        uniqueness.
    """
    def __init__(self):
        self._count = 0
        self._registered_ids = set()

    def register(self, seq_id: str) -> None:
        """
        Registers a new sequence ID, ensuring it is unique.

        Parameters
        ----------
        seq_id : str
            The new sequence ID to register.

        Raises
        ------
        ValueError
            If the sequence ID has already been registered.

        """
        if seq_id in self._registered_ids:
            raise ValueError(f"Sequence ID {seq_id} has already been registered")
        self._registered_ids.add(seq_id)

    def generate(self) -> str:
        """
        Generates a new unique sequence ID.

        Returns
        -------
        str
            A new unique sequence ID.
        """
        self._count += 1
        while True:
            seq_id = num_to_letters(self._count)
            if seq_id not in self._registered_ids:
                return seq_id
            self._count += 1

    def reset(self) -> None:
        """
        Resets the `IDRegister` object.

        Notes
        -----
        The ids and register states of corresponding sequence objects are
        not affected.
        """
        self._count = 0
        self._registered_ids = set()
