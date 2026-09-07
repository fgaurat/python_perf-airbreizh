import pytest

from salut.salutation import formule, saluer


@pytest.mark.parametrize(
    ("heure", "attendue"),
    [
        pytest.param(0, "Bonjour", id="minuit"),
        pytest.param(11, "Bonjour", id="fin_de_matinee"),
        pytest.param(12, "Bon après-midi", id="midi"),
        pytest.param(17, "Bon après-midi", id="fin_d_apres_midi"),
        pytest.param(18, "Bonsoir", id="18h"),
        pytest.param(23, "Bonsoir", id="23h"),
    ],
)
def test_formule(heure, attendue):
    assert formule(heure) == attendue


@pytest.mark.parametrize("heure", [-1, 24])
def test_formule_refuse_une_heure_invalide(heure):
    with pytest.raises(ValueError):
        formule(heure)


class HorlogeFixe:
    def __init__(self, heure):
        self._heure = heure

    def heure(self):
        return self._heure


def test_saluer_utilise_l_horloge_recue():
    assert saluer("Ada", HorlogeFixe(9)) == "Bonjour, Ada !"
    assert saluer("Ada", HorlogeFixe(21)) == "Bonsoir, Ada !"
