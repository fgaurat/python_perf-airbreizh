import pytest

from geo.rectangle import Rectangle


@pytest.fixture(autouse=True)
def compteur_remis_a_zero():
    """Rectangle._cpt est un état global : chaque test repart de zéro.

    autouse=True : la fixture s'applique à tous les tests du dossier sans
    qu'ils aient à la demander.
    """
    Rectangle._cpt = 0
    yield
    Rectangle._cpt = 0
