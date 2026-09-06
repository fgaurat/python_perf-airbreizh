from calcul.operations import additionner, arrondir, diviser, moyenne, puissance, racine


def test_additionner_1():
    assert additionner(2, 3) == 5


def test_additionner_2():
    assert additionner(10, 20) == 30


def test_additionner_3():
    assert additionner(100, 200) == 300


def test_diviser():
    assert diviser(10, 4) == 2.5


def test_puissance():
    assert puissance(2, 10) == 1024


def test_racine():
    assert racine(16) == 4


def test_arrondir():
    assert arrondir(3.14159, 2) == 3.14


def test_moyenne():
    assert moyenne([1, 2, 3]) == 2
