from typing import Literal
from pydantic import BaseModel


class Pivot(BaseModel):
    journal: str
    journal_clean: str
    titre: str
    complement: str
    annee: int
    mois: int
    jour: int
    heure: int
    minute: int
    seconde: int
    date: str
    epoch: int
    auteur: str
    texte: str
    keywords: str
    langue: str

    def __hash__(self):
        return hash((self.journal, self.date, self.titre))
