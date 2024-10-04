"""
Permet d'exporter depuis le terminal python de Qgis, les couches segments et compositions vers la Dropbox.
Il faut pour se faire que le dossier /Dropbox/skitourenguru/Routes soit sur la branche principale (main).
"""

import subprocess
from pygit2 import Repository
from qgis.utils import iface

dossier = "/home/ulysse/Dropbox/skitourenguru/Routes/France"
compo_name = "France_Compositions.geojson"
segments_name = "France_Segments.geojson"
db = """host=localhost
                dbname=France_Alpes
                user=postgres
                password=postgres
                port=5432
     """


repo = Repository(dossier)
head = repo.head.name

if head == "refs/heads/main":

    statement = """
        SELECT id, start, stop, routes, mdiff, segments::text
        FROM compositions
        WHERE importance='0' AND NOT segments = '{}'
        ORDER BY id
    """

    #Exporter la couche composition avec ogr2ogr
    command = f"ogr2ogr -sql \"{statement}\" -nln \"compositions\" {dossier}/{compo_name} PG:\"{db}\""

    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print("La commande a échoué avec le code de sortie : ", e.returncode)

    statement = """
        SELECT id, geom
        FROM segments
        WHERE importance='0'
        ORDER BY id
    """

    #Exporter la couche segments
    command = f"ogr2ogr -sql \"{statement}\" -nln \"segments\" {dossier}/{segments_name} PG:\"{db}\""

    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError as e:
        print("La commande a échoué avec le code de sortie : ", e.returncode)

    iface.messageBar().pushMessage("Couches compositions et segments exportées sur la branche principale.")

else:
    iface.messageBar().pushMessage("Les couches compositions et segments n'ont pas été exportées car le dossier est sur la branche Backup, pour changer : 'git checkout main' ")
