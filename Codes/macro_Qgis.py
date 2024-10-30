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
        subprocess.run(push, shell=True)

        drop_pull = f"cd {dropbox} && git pull"
        subprocess.run(drop_pull, shell=True)

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
"""
command = "curl https://download.skitourenguru.com/public/Warnings.log --output /home/ulysse/Data/Vecteurs/Skitourenguru_Public/Warnings.log"

try:
    subprocess.check_call(command, shell=True)
except subprocess.CalledProcessError as e:
    print("La commande a échoué avec le code de sortie : ", e.returncode)


no_problems = r"Had no problems"
problems = r"Had problems with (\d+) routes"
path = "/home/ulysse/Data/Vecteurs/Skitourenguru_Public"
logs = "/home/ulysse/Code/logs"
today = datetime.date.today()


with open(f"{logs}/Warnings_short.log", "w") as f:
    f.write("")
cur.execute("TRUNCATE TABLE Alerte")
conn.commit()

segid = r"Segment (\d+) is not"
regex_arret = r"Created"

with open(f"{path}/Warnings.log", "r") as f:
    texte = f.read()

segids = []
match_arret = re.search(regex_arret, texte, re.DOTALL)
if match_arret:

    texte_avant_arret = texte[:match_arret.start()]
    for match in re.finditer(segid, texte_avant_arret):
        segids.append(match.group(1))

else:
    for match in re.finditer(regex_interessant, texte):
        occurrences.append(match.group())

s = collections.Counter(segids)
for nombre, frequence in sorted(s.items()):
    if frequence < 2:
        print(f'Problème avec le segment {nombre} dans {frequence} itinéraire.')
        with open(f"{logs}/Warnings_short.log", "a") as f:
            f.write(f'{today} : Problème avec le segment {nombre} dans {frequence} itinéraire.\n')
    else:
        print(f'Problème avec le segment {nombre} dans {frequence} itinéraires.')
        with open(f"{logs}/Warnings_short.log", "a") as f:
            f.write(f'{today} : Problème avec le segment {nombre} dans {frequence} itinéraires.\n')

    cur.execute(f"INSERT INTO Alerte (id, geom) SELECT {nombre}, geom FROM segments WHERE {nombre} = segments.id ")
    conn.commit()


with open(f"{path}/Warnings.log", "r") as f:
    content = f.read()

if re.search(no_problems, content):
    iface.messageBar().pushMessage("Warnings ", "Aucun problème trouvé", level=Qgis.Success, duration=6)
elif re.search(problems, content):
    match = re.search(problems, content)
    if match:
        nombre = match.group(1)
    def showError():
        subprocess.run(["gnome-text-editor", f"{logs}/Warnings_short.log"])

    widget = iface.messageBar().createMessage("Warnings ", f"Problème avec {nombre} routes.")
    button = QPushButton(widget)
    button.setText("Voir")
    button.pressed.connect(showError)
    widget.layout().addWidget(button)
    iface.messageBar().pushWidget(widget, Qgis.Warning)
else:
    iface.messageBar().pushMessage("Warnings ", "Aucune correspondance trouvé. Vérifiez que Warnings.log soit bien téléchargé", level=Qgis.Info, duration=6)
"""
cur.close()
conn.close()
