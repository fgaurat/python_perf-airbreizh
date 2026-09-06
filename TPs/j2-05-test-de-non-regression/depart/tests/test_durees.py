from temps.durees import analyser, formater, total


def test_zero():
    assert formater(0) == "0 s"


def test_secondes():
    assert formater(5) == "5 s"


def test_minutes_et_secondes():
    assert formater(65) == "1 min 05 s"


def test_une_heure():
    assert formater(3600) == "1 h"


def test_heures_minutes_secondes():
    assert formater(3725) == "1 h 02 min 05 s"


def test_presque_un_jour():
    assert formater(86399) == "23 h 59 min 59 s"


def test_analyser():
    assert analyser("1 h 02 min 05 s") == 3725


def test_total():
    assert total(["1 h", "30 min", "45 s"]) == "1 h 30 min 45 s"
