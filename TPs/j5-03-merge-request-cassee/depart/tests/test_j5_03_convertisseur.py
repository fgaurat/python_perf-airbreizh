"""Tests du convertisseur."""

import pytest

from convertisseur import (
    ConversionImpossible,
    UniteInconnue,
    convertir,
    convertir_longueur,
    convertir_temperature,
)

# --- Températures ------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("valeur", "de", "vers", "attendu"),
    [
        pytest.param(0, "C", "F", 32.0, id="gel_en_fahrenheit"),
        pytest.param(100, "C", "F", 212.0, id="ebullition_en_fahrenheit"),
        pytest.param(-40, "C", "F", -40.0, id="le_point_commun"),
        pytest.param(98.6, "F", "C", 37.0, id="corps_humain"),
        pytest.param(0, "C", "K", 273.15, id="gel_en_kelvin"),
        pytest.param(0, "K", "C", -273.15, id="zero_absolu"),
        pytest.param(300, "K", "F", 80.33, id="kelvin_vers_fahrenheit"),
        pytest.param(21.5, "C", "C", 21.5, id="identite"),
    ],
)
def test_temperatures(valeur, de, vers, attendu):
    assert convertir_temperature(valeur, de, vers) == pytest.approx(attendu)


def test_unite_de_temperature_inconnue():
    with pytest.raises(UniteInconnue, match="'R'"):
        convertir_temperature(10, "C", "R")


# --- Longueurs, grandes unités ----------------------------------------------------------


@pytest.mark.parametrize(
    ("valeur", "de", "vers", "attendu"),
    [
        pytest.param(1, "km", "m", 1000.0, id="km_vers_m"),
        pytest.param(1500, "m", "km", 1.5, id="m_vers_km"),
        pytest.param(1, "mi", "km", 1.6093, id="mile_vers_km"),
        pytest.param(10, "km", "mi", 6.2137, id="km_vers_mile"),
        pytest.param(1, "nmi", "km", 1.852, id="nautique_vers_km"),
        pytest.param(100, "km", "nmi", 53.9957, id="km_vers_nautique"),
        pytest.param(1, "nmi", "mi", 1.1508, id="nautique_vers_mile"),
        pytest.param(42.195, "km", "km", 42.195, id="identite"),
    ],
)
def test_longueurs(valeur, de, vers, attendu):
    assert convertir_longueur(valeur, de, vers) == pytest.approx(attendu)


# --- Longueurs, petites unités ------------------------------------------------------------


def test_pouce_vers_centimetre():
    assert convertir_longueur(1, "in", "cm") == pytest.approx(2.54)


def test_pied_vers_metre():
    assert convertir_longueur(1, "ft", "m") == pytest.approx(0.3048)


def test_millimetre_vers_metre():
    assert convertir_longueur(1, "mm", "m") == pytest.approx(0.001)


def test_centimetre_vers_pouce():
    assert convertir_longueur(2.54, "cm", "in") == pytest.approx(1.0)


def test_unite_de_longueur_inconnue():
    with pytest.raises(UniteInconnue, match="'yd'"):
        convertir_longueur(1, "yd", "m")


# --- Le point d'entrée -----------------------------------------------------------------------


def test_convertir_choisit_la_famille():
    assert convertir(1, "km", "m") == 1000.0
    assert convertir(0, "C", "F") == 32.0


def test_convertir_refuse_de_melanger_les_familles():
    with pytest.raises(ConversionImpossible, match="pas de la même famille"):
        convertir(1, "km", "C")


def test_convertir_unite_inconnue():
    with pytest.raises(UniteInconnue, match="'parsec'"):
        convertir(1, "parsec", "km")
