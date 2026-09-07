from salut.salutation import saluer


def test_le_matin():
    assert saluer("Ada") == "Bonjour, Ada !"
