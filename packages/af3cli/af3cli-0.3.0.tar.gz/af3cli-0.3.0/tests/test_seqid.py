import pytest

from af3cli.seqid import num_to_letters, IDRegister


@pytest.mark.parametrize("num,letters", [
    (1, "A"), (2, "B"), (3, "C"), (26, "Z"),
    (27, "AA"), (28, "AB"), (52, "AZ"), (53, "BA"),
    (703, "AAA"), (704, "AAB")
])
def test_num_to_letters(num: int, letters: str) -> None:
    assert num_to_letters(num) == letters


@pytest.fixture(scope="module")
def register() -> IDRegister:
    return IDRegister()


@pytest.mark.parametrize("letter", [
    "A", "B", "C", "D"
])
def test_id_register(register: IDRegister, letter: str) -> None:
    assert register.generate() == letter


@pytest.mark.parametrize("letter", [
    "F", "G", "H", "I"
])
def test_id_register_fill(register: IDRegister, letter: str) -> None:
    register.register(letter)
    assert letter in register._registered_ids
    assert register._count == 4


@pytest.mark.parametrize("letter", [
    "E", "J", "K", "L", "M"
])
def test_id_register_filled(register: IDRegister, letter: str) -> None:
    assert register.generate() == letter


@pytest.mark.parametrize("letter", [
    "N", "NN", "NNN", "NNNN"
])
def test_id_register_multiple_letters(
        register: IDRegister,
        letter: str
) -> None:
    register.register(letter)
    assert letter in register._registered_ids


def test_id_register_reset(register: IDRegister) -> None:
    register.reset()
    assert len(register._registered_ids) == 0
    assert register._count == 0
