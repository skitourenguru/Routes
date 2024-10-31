import psycopg2
from pygit2 import Repository
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *
import subprocess
import os
from PyQt5.QtWidgets import QPushButton
import re
import collections
import datetime
import requests

def saveProject():
    dropbox = '/home/ulysse/Dropbox/skitourenguru/Routes/France'
    dossier = '/home/ulysse/Data/Vecteurs/Routes/France'
    repo = Repository(dossier)
    head = repo.head.name

    if head == "refs/heads/backup":

        db = """host=localhost
                dbname=France_Alpes
                user=postgres
                password=postgres
                port=5432"""

        statement = """
        SELECT id, start, stop, routes, mdiff, importance, REPLACE(REPLACE(segments::text, '{', ''), '}', '') as segments, massif
        FROM compositions
        ORDER BY id
        """
        #Exporter la couche composition avec ogr2ogr
        command = f"ogr2ogr -sql \"{statement}\" -nln \"compositions\" {dossier}/France_Compositions.geojson PG:\"{db}\""

        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as e:
            print("La commande a échoué avec le code de sortie : ", e.returncode)

        statement = """
        SELECT fid, id, importance, massif, geom
        FROM segments
        ORDER BY id
        """
        #Exporter la couche segments
        command = f"ogr2ogr -sql \"{statement}\" -nln \"segments\" {dossier}/France_Segments.geojson PG:\"{db}\""

        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as e:
            print("La commande a échoué avec le code de sortie : ", e.returncode)

        push = f"cd {dossier} && git commit -a -m \"backup\" && git push"
        subprocess.run(push, shell=True, timeout=10)

        drop_pull = f"cd {dropbox} && git pull"
        subprocess.run(drop_pull, shell=True, timeout=10)

        iface.messageBar().pushMessage("Couches compositions et segments exportées et poussées sur la branche 'backup' avec succès.")
    else:
        iface.messageBar().pushMessage("Layers Segments & Compositions not exported because you're on Main branch. Please switch to Backup : 'git checkout backup' ")


#Get connexion to the Database
conn = psycopg2.connect(
    host = "localhost",
    database = "France_Alpes",
    user = "postgres",
    password = "postgres" )

# Change the type of segments column in compositions table to be accepted as string by QGIS but to be array in reality
cur = conn.cursor()
cur.execute("""
    ALTER TABLE compositions
            ALTER segments TYPE TEXT USING array_to_string(segments, ','); """)
conn.commit()

# Remove compositions layer of Qgis Legend interface
project = QgsProject.instance()
layer = project.mapLayersByName("compositions")[0]
layer = layer.id()
project.removeMapLayer(layer)

# Get connexion to PostgreSQL
uri = QgsDataSourceUri()
uri.setConnection("localhost", "5432", "France_Alpes", "postgres", "postgres")
uri.setDataSource("public", "compositions", "geom")

# Find the place where to insert the new compositions layer
root = QgsProject.instance().layerTreeRoot()
root = root.findGroup("Postgres")
# And Insert it
new = QgsVectorLayer(uri.uri(), "compositions", "postgres")
QgsProject.instance().addMapLayer(new, False)
root.insertLayer(3, new)

# Change again the type, String to Array.

cur.execute("""
    ALTER TABLE compositions
            ALTER segments TYPE INTEGER[] USING string_to_array(segments, ',')::int[]
""")
conn.commit()

# Open the attribute table from Compositions.
layer = QgsProject.instance().mapLayersByName('compositions')[0]
iface.showAttributeTable(layer)

############################################################################################
########################### Check if there is Warnings #####################################
############################################################################################

def truncate(logs : str) -> None:
    # Avant de chercher les warnings, vider les logs et alertes de la dernière fois.
    with open(f"{logs}/Warnings_short.log", "w") as f:
        f.write("")
    cur.execute(f"TRUNCATE TABLE Alerte")

def find_warnings(texte: str, stop_here: str, capture_that: str) -> tuple[int,int]:
    # Chercher les warnings dans le fichier téléchargé aujourd'hui.
    segids = []
    frequence = 0
    segments_problematiques = 0

    match_arret = re.search(stop_here, texte, re.DOTALL)
    if match_arret:
        texte_avant_arret = texte[:match_arret.start()]
        for match in re.finditer(capture_that, texte_avant_arret):
            segids.append(match.group(1))

    if segids:
        s = collections.Counter(segids)
        for segments_id, freq in sorted(s.items()):
            segments_problematiques = int(segments_id)
            frequence = int(freq)

    return segments_problematiques, frequence


def openProject():
    path_to_warn = "/home/ulysse/Data/Vecteurs/Skitourenguru_Public"
    logs = "/home/ulysse/Code/logs"
    today = datetime.date.today()
    # Expressions régulières :
    no_problems = r"Had no problems"
    problems = r"Had problems with (\d+) routes"
    stop_here = r"Created \d+ new routes"
    capture_that = r"Segment (\d+) is not well connected"

    try :
        download_warnings = "curl https://download.skitourenguru.com/public/Warnings.log --output /home/ulysse/Data/Vecteurs/Skitourenguru_Public/Warnings.log"
        subprocess.run(download_warnings, shell=True, timeout=5)

        truncate(logs)

        with open(f"{path_to_warn}/Warnings.log", "r") as f:
            texte = f.read()
        if re.search(no_problems, texte):
            iface.messageBar().pushMessage("Warnings ", "Aucun problème trouvé", level=Qgis.Success, duration=6)

        else:
            segments_problematiques, frequence = find_warnings(texte, stop_here, capture_that)

            if frequence > 0:
                if frequence == 1:
                    message = f"Problème avec le segment {segments_problematiques}"
                else:
                    message = f"Problème avec le segment {segments_problematiques} dans {frequence} itinéraires."

                with open(f"{logs}/Warnings_short.log", "a") as f:
                    f.write(f'{today} : {message}.\n')
                print(message)

                def showError():
                    subprocess.run(["gte", f"{logs}/Warnings_short.log"])

                widget = iface.messageBar().createMessage("Warnings ", f"Problème avec {segments_problematiques} routes.")
                button = QPushButton(widget)
                button.setText("Voir")
                button.pressed.connect(showError)
                widget.layout().addWidget(button)
                iface.messageBar().pushWidget(widget, Qgis.Warning)

                cur.execute(f"INSERT INTO Alerte (id, geom) SELECT {segments_problematiques}, geom FROM segments WHERE {segments_problematiques} = segments.id ")
                conn.commit()

    except subprocess.TimeoutExpired:
        iface.messageBar().pushMessage("Erreur", "Timeout lors du téléchargement du fichier Warnings.log",
                                        level=Qgis.MessageLevel.Critical)
    except FileNotFoundError:
        iface.messageBar().pushMessage("Erreur", "Impossible de trouver le fichier Warnings.log",
                                        level=Qgis.MessageLevel.Critical)
    except Exception as e:
        iface.messageBar().pushMessage("Erreur", f"Une erreur inattendue s'est produite: {str(e)}",
                                        level=Qgis.MessageLevel.Critical)

    finally:
        cur.close()
        conn.close()
