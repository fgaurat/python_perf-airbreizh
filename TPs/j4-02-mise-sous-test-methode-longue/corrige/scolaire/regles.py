"""Les règles du bulletin, une fonction chacune. Aucune I/O, aucun print.

Les comportements figés ici incluent les bugs relevés dans BUGS.md : un
refactoring ne corrige rien, il rend corrigeable.
"""

from collections.abc import Mapping, Sequence

from scolaire.modele import (
    BONUS_MAX,
    COEF_MATIERE_INCONNUE,
    COEFFICIENTS,
    ECART_PROGRESSION,
    NIVEAUX,
    NOTE_SUR,
    OPTIONS,
    SEUIL_ABSENCES,
    SEUIL_AVERTISSEMENT,
    SEUIL_COMPLIMENTS,
    SEUIL_ENCOURAGEMENTS,
    SEUIL_FELICITATIONS,
    Absences,
    ErreurBulletin,
    MoyenneMatiere,
    Periode,
)


def valider_eleve(eleve: Mapping) -> str:
    """Vérifie l'identifiant et retourne la classe (6e par défaut)."""
    if not eleve.get("id"):
        raise ErreurBulletin("identifiant manquant")
    classe = eleve.get("classe", "6e")
    if classe not in NIVEAUX:
        raise ErreurBulletin(f"classe inconnue : {classe}")
    return classe


def analyser_trimestre(trimestre: str) -> Periode:
    """'2026-T1' -> Periode(2026, 1)."""
    if len(trimestre) != 7 or trimestre[4:6] != "-T":
        raise ErreurBulletin(f"trimestre invalide : {trimestre}")
    try:
        periode = Periode(int(trimestre[:4]), int(trimestre[6:]))
    except ValueError:
        raise ErreurBulletin(f"trimestre invalide : {trimestre}") from None
    if periode.numero not in (1, 2, 3):
        raise ErreurBulletin(f"trimestre invalide : {trimestre}")
    if periode.annee < 2000:
        raise ErreurBulletin(f"annee invalide : {periode.annee}")
    return periode


def moyenne_matiere(matiere: str, notes: Sequence[Mapping]) -> MoyenneMatiere | None:
    """Moyenne pondérée des notes ramenées sur 20, ou None si aucune note exploitable."""
    total = 0.0
    poids = 0.0
    nb_notes = 0
    for note in notes:
        valeur = note.get("valeur")
        if valeur is None:
            continue
        sur = note.get("sur", NOTE_SUR)
        if valeur < 0:
            raise ErreurBulletin(f"note négative en {matiere}")
        if sur <= 0:
            raise ErreurBulletin(f"barème invalide en {matiere}")
        coef = note.get("coef", 1)
        total += valeur / sur * NOTE_SUR * coef
        poids += coef
        nb_notes += 1
    if poids == 0:
        return None
    return MoyenneMatiere(matiere, round(total / poids, 2), nb_notes)


def moyennes_par_matiere(notes: Mapping[str, Sequence[Mapping]]) -> list[MoyenneMatiere]:
    """Une entrée par matière notée, par ordre alphabétique de matière."""
    resultats = [moyenne_matiere(matiere, liste) for matiere, liste in sorted(notes.items())]
    return [m for m in resultats if m is not None]


def moyenne_generale(moyennes: Mapping[str, float]) -> float:
    """Moyenne des matières hors options, pondérée par COEFFICIENTS."""
    somme = 0.0
    somme_coefs = 0.0
    for matiere, moyenne in moyennes.items():
        if matiere in OPTIONS:
            continue
        coef = COEFFICIENTS.get(matiere, COEF_MATIERE_INCONNUE)
        somme += moyenne * coef
        somme_coefs += coef
    if somme_coefs == 0:
        raise ErreurBulletin("aucune note")
    return somme / somme_coefs


def bonus_options(moyennes: Mapping[str, float]) -> float:
    """Points de bonus des options au-dessus de 10, plafonnés à BONUS_MAX."""
    bonus = 0.0
    for option, taux in OPTIONS.items():
        if option in moyennes and moyennes[option] > 10:
            bonus += (moyennes[option] - 10) * taux
    return min(bonus, BONUS_MAX)


def mention(moyenne_finale: float) -> str:
    if moyenne_finale > SEUIL_FELICITATIONS:
        return "Félicitations"
    if moyenne_finale > SEUIL_COMPLIMENTS:
        return "Compliments"
    if moyenne_finale > SEUIL_ENCOURAGEMENTS:
        return "Encouragements"
    if moyenne_finale < SEUIL_AVERTISSEMENT:
        return "Avertissement travail"
    return ""


def rang(moyenne_finale: float, moyennes_classe: Sequence[float]) -> int:
    return 1 + sum(1 for m in moyennes_classe if m >= moyenne_finale)


def compter_absences(absences: Sequence) -> Absences:
    """Chaque entrée vaut une demi-journée, quel que soit son format."""
    demi_journees = len(absences)
    return Absences(demi_journees, demi_journees > SEUIL_ABSENCES)


def tendance(moyenne_finale: float, precedente: float) -> str:
    ecart = moyenne_finale - precedente
    if ecart >= ECART_PROGRESSION:
        return "en progrès"
    if ecart <= -ECART_PROGRESSION:
        return "en baisse"
    return "stable"


def appreciation(la_mention: str, la_tendance: str, avertissement_assiduite: bool) -> str:
    if la_mention == "Félicitations":
        texte = f"Excellent trimestre, {la_tendance}."
    elif la_mention in ("Compliments", "Encouragements"):
        texte = f"Bon trimestre, {la_tendance}. Continuez ainsi."
    elif la_mention == "Avertissement travail":
        texte = f"Résultats insuffisants, {la_tendance}. Un effort important est attendu."
    else:
        texte = f"Trimestre correct, {la_tendance}."
    if avertissement_assiduite:
        texte += " L'assiduité doit s'améliorer."
    return texte
