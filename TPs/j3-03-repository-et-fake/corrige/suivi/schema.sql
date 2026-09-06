CREATE TABLE taches (
    id        INTEGER PRIMARY KEY,
    titre     TEXT    NOT NULL,
    projet    TEXT    NOT NULL,
    assignee  TEXT    NOT NULL,
    creee_le  TEXT    NOT NULL,   -- ISO 8601 : 2026-09-01
    echeance  TEXT    NOT NULL,
    terminee  INTEGER NOT NULL DEFAULT 0
);
