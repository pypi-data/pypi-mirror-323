from commonlib.models import Pair


def test_keyword_creation() -> None:
    p = Pair(
        first=1,
        second=2,
    )
    assert p.first == 1
    assert p.second == 2


def test_creation_from_values() -> None:
    p = Pair(1, 2)
    assert p[0] == 1
    assert p[1] == 2


def test_creation_from_iterable() -> None:
    p = Pair((1, 2))
    assert p[0] == 1
    assert p[1] == 2

    p = Pair([1, 2])
    assert p[0] == 1
    assert p[1] == 2


class Complex:
    def __init__(self, a: int, b: str) -> None:
        self.a = a
        self.b = b


def test_complex() -> None:
    comp1 = Complex(1, '1')
    comp2 = Complex(2, '2')
    p = Pair(comp1, comp2)
    p_a = Pair(1, 2)
    p_b = Pair('1', '2')
    assert p.a == p_a
    assert p.b == p_b
