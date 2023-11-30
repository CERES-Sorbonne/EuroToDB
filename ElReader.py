import json
from pathlib import Path
from typing import Any
from sys import stderr

import pandas as pd
from tqdm.auto import tqdm
import psycopg2
from psycopg2 import errors
from psycopg2.errorcodes import UNIQUE_VIOLATION

from models import Pivot


class ElReader:
    def __init__(self, creds: str | Path | dict):
        if isinstance(creds, str):
            creds = Path(creds)

        if isinstance(creds, Path):
            with creds.open("r") as f:
                creds = json.load(f)

        if not isinstance(creds, dict):
            raise TypeError(f"Type {type(creds)} non supporté.")

        self.creds = creds
        self.conn = (psycopg2.connect(**creds))
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id serial PRIMARY KEY,
            journal varchar,
            journal_clean varchar,
            titre varchar,
            complement varchar,
            annee integer,
            mois integer,
            jour integer,
            heure integer,
            minute integer,
            seconde integer,
            date varchar,
            epoch date,
            auteur varchar,
            texte varchar,
            keywords varchar,
            langue varchar,
            hash varchar
        );
        CREATE INDEX IF NOT EXISTS articles_journal_clean_idx ON articles (journal_clean);
        CREATE INDEX IF NOT EXISTS articles_journal_idx ON articles (journal);
        CREATE UNIQUE INDEX IF NOT EXISTS articles_hash_idx ON articles (hash);
        """)
        self.conn.commit()
        self.cursor.close()

    def insert(self, article: Pivot, verbose: bool = False):
        if not isinstance(article, Pivot):
            raise TypeError("Veuillez fournir un objet de type Pivot.")

        cursor = self.conn.cursor()
        try:
            cursor.execute(
                f"""
            INSERT INTO articles (
                journal,
                journal_clean,
                titre,
                complement,
                annee,
                mois,
                jour,
                heure,
                minute,
                seconde,
                date,
                epoch,
                auteur,
                texte,
                keywords,
                langue,
                hash
            ) VALUES (
                %s, 
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,      
                %s,
                to_timestamp(%s),
                %s,
                %s,
                %s,
                %s,
                md5(%s)
            );
            """,
                (
                    article.journal,
                    article.journal_clean,
                    article.titre,
                    article.complement,
                    article.annee,
                    article.mois,
                    article.jour,
                    article.heure,
                    article.minute,
                    article.seconde,
                    article.date,
                    article.epoch,
                    article.auteur,
                    article.texte,
                    article.keywords,
                    article.langue,
                    article.titre + article.date + article.journal + article.texte
                )
            )
            self.conn.commit()
        except errors.lookup(UNIQUE_VIOLATION):
            if verbose:
                tqdm.write(
                    f"""Article {article.titre} déjà présent dans la base de données.
({article.journal = }\t {article.date = }\t {article.auteur = })""",
                    file=stderr
                )
            self.conn.rollback()
        cursor.close()

    def insert_file(self, file: str | Path | list[dict] | dict, verbose: bool = False):
        if isinstance(file, str):
            file = Path(file)

        if isinstance(file, Path):
            with file.open("r", encoding="utf-8") as f:
                file = json.load(f)

        file = self.dict_or_df(file)

        if isinstance(file, list):
            for article in tqdm(file):
                self.insert(Pivot(**article))
            return

        if isinstance(file, dict):
            self.insert(Pivot(**file))
            return

        raise TypeError(f"Type {type(file)} non supporté.")

    def dict_or_df(self, dict_: dict[str, dict[str, Any]] | list):
        if isinstance(dict_, list):
            return dict_

        if not isinstance(dict_, dict):
            raise TypeError(f"Type {type(dict_)} non supporté.")

        try:
            [int(key) for key in dict_.keys()]
            return list(dict_.values())
        except ValueError:
            return dict_

    def get_articles(self, journal: str = None, journal_clean: str = None, date: str = None, titre: str = None,
                     auteur: str = None, texte: str = None, keywords: str = None, langue: str = None, limit: int = None,
                     offset: int = None):
        cursor = self.conn.cursor()
        query = f"""
        SELECT * FROM articles
        WHERE TRUE
        """
        q = []
        if journal:
            q += f"journal = '{journal}'"
        if journal_clean:
            q += f"journal_clean = '{journal_clean}'"
        if date:
            q += f"date = '{date}'"
        if titre:
            q += f"titre = '{titre}'"
        if auteur:
            q += f"auteur = '{auteur}'"
        if texte:
            q += f"texte = '{texte}' AND "
        if keywords:
            q += f"keywords = '{keywords}'"
        if langue:
            q += f"langue = '{langue}'"
        if q:
            query += " AND ".join(q)

        if limit:
            query += f"\nLIMIT {limit}"

        if offset:
            query += f"\nOFFSET {offset}"

        query += ";"
        cursor.execute(query)
        articles = cursor.fetchall()
        cursor.close()

        return articles

    def get_articles_df(self, journal: str = None, journal_clean: str = None, date: str = None, titre: str = None,
                        auteur: str = None, texte: str = None, keywords: str = None, langue: str = None,
                        limit: int = None, offset: int = None):
        articles = self.get_articles(journal, journal_clean, date, titre, auteur, texte, keywords, langue, limit,
                                     offset)
        return pd.DataFrame(
            articles,
            columns=["id", "journal", "journal_clean", "titre", "complement", "annee", "mois", "jour", "heure",
                     "minute", "seconde", "date", "epoch", "auteur", "texte", "keywords", "langue", "hash"]
        )

    def see(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM articles LIMIT 10;")
        articles = cursor.fetchall()
        cursor.close()
        return articles

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, "conn"):
            self.conn.close()

    def __repr__(self):
        return f"ElReader({self.creds})"

    def __str__(self):
        return f"ElReader({self.creds})"

    def __iter__(self):
        return self.see().__iter__()

    def __next__(self):
        return self.see().__next__()


def main():
    with open("creds.json", "r") as f:
        creds = json.load(f)

    with ElReader(creds) as reader:
        print(reader.see())

    with ElReader(creds) as reader:
        print(reader.get_articles_df(limit=10))

    with ElReader(creds) as reader:
        print(reader.get_articles_df(limit=10, offset=10))


if __name__ == "__main__":
    main()
