import time
from pathlib import Path
from time import sleep
import json

from ElReader import ElReader

def main(credsfile: str | Path | dict, folder_to_watch : str | Path, folder_to_stash: str | Path):
    if isinstance(credsfile, str):
        credsfile = Path(credsfile)

    if isinstance(folder_to_watch, str):
        folder_to_watch = Path(folder_to_watch)

    if isinstance(folder_to_stash, str):
        folder_to_stash = Path(folder_to_stash)

    assert (
    credsfile.exists()
    and credsfile.is_file()
    and credsfile.stat().st_size > 0
    ), f"{credsfile.name} absent ou vide."

    try:
        with credsfile.open("r", encoding="utf-8") as f:
            creds = json.load(f)

        for key in ("host", "port", "database", "user", "password"):
            assert key in creds, f"Clé {key} absente de creds.json."

    except json.JSONDecodeError:
        print(f"{credsfile.name} invalide.")
        raise

    reader = ElReader(creds)

    while True:
        files = set(folder_to_watch.glob("*.json")).difference(set(folder_to_stash.glob("*.json")))
        for file in files:
            start = time.perf_counter()
            print(f"Insertion de {file.name}...")  # , end=" ")
            try:
                with file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                continue  # Ensure file is not being written to

            reader.insert_file(data)
            print(f"=> terminée en {time.perf_counter() - start:.2f} secondes.")

            file.rename(folder_to_stash / file.name)

        else:
            sleep(60)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()

    parser.add_argument("credsfile", help="Chemin vers le fichier creds.json", type=Path)  # , required=True)
    parser.add_argument("folder_to_watch", help="Dossier à surveiller", type=Path)  # , required=True)
    parser.add_argument("folder_to_stash", help="Dossier où déplacer les fichiers traités", type=Path)  # , required=True)

    args = parser.parse_args()

    main(args.credsfile, args.folder_to_watch, args.folder_to_stash)

