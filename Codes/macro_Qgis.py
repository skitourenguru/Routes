from contextlib import contextmanager
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

CONFIG = {
    'database': {
        'host': 'localhost',
        'database': 'France_Alpes',
        'user': 'postgres',
        'password': 'postgres',
        'port': 5432
    },
    'paths': {
        'dropbox': '/home/ulysse/Dropbox/skitourenguru/Routes/France',
        'dossier': '/home/ulysse/Data/Vecteurs/Routes/France',
    }
}

class DatabaseConnexion:
    @contextmanager
    def get_db_connexion(self):
        conn = psycopg2.connect(**CONFIG['database'])
        try:
            yield conn
        finally:
            conn.close()

    def check_column_type(self):
        with self.get_db_connexion() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT data_type
                    FROM information_schema.columns
                    WHERE table_name = 'compositions'
                    AND column_name = 'segments';
                    """)
                result = cur.fetchone()
                return result [0] if result else None


    def array_to_text(self):
        with self.get_db_connexion() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    ALTER TABLE compositions
                    ALTER segments TYPE TEXT
                    USING array_to_string(segments, ',');
                """)
                conn.commit()

    def text_to_array(self):
        with self.get_db_connexion() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    ALTER TABLE compositions
                    ALTER segments TYPE INTEGER[]
                    USING string_to_array(segments, ',')::int[];
                """)
                conn.commit()

class QgisHandler:
    def __init__(self):
        self.project = QgsProject.instance()
        self.iface = iface

    def remove_layer(self, layer_name):
        """Supprime une couche du projet QGIS par son nom."""
        if self.project:
            layers = self.project.mapLayersByName(layer_name)
            if layers:
                self.project.removeMapLayer(layers[0].id())
                return True
        return False

    def create_postgres_layer(self, table_name, geometry_column="geom"):

        uri = QgsDataSourceUri()
        uri.setConnection(
            CONFIG['database']['host'],
            str(CONFIG['database']['port']),
            CONFIG['database']['database'],
            CONFIG['database']['user'],
            CONFIG['database']['password']
        )
        uri.setDataSource("public", table_name, geometry_column)

        layer = QgsVectorLayer(uri.uri(), table_name, "postgres")
        if not layer.isValid():
            self.iface.messageBar().pushMessage(
                "Erreur",
                f"La couche {table_name} n'a pas pu être chargée",
                level=Qgis.Critical
            )
            return None
        return layer

    def add_layer_to_group(self, layer, group_name, position=None):
        """Ajoute une couche à un groupe spécifique."""
        if self.project:
            root = self.project.layerTreeRoot()
            group = root.findGroup(group_name)

            if group:
                self.project.addMapLayer(layer, False)
                if position is not None:
                    group.insertLayer(position, layer)
                else:
                    group.addLayer(layer)
                return True
            else:
                # Si le groupe n'existe pas, ajouter directement au projet
                self.project.addMapLayer(layer)
                return True
        return False

    def show_attribute_table(self, layer):
        """Affiche la table d'attributs d'une couche."""
        if layer and layer.isValid():
            self.iface.showAttributeTable(layer)
            return True
        return False

class GitHandler:
    def __init__(self):
        self.dropbox = CONFIG['paths']['dropbox']
        self.data_dir = CONFIG['paths']['data']
        self.repo = Repository(self.data_dir)

    def backup_data(self):
        if self.repo.head.name == "refs/heads/backup":
            self._export_compositions()
            self._export_segments()
            self._push_changes()
            return True
        return False

    def _export_compositions(self):
        statement = """SELECT id, start, stop, routes, mdiff, importance, REPLACE(REPLACE(segments::text, '{', ''), '}', '') as segments, massif FROM compositions ORDER BY id"""
        self._export_layer("compositions", statement)

    def _export_segments(self):
        statement = """SELECT fid, id, importance, massif, geom FROM segments ORDER BY id"""
        self._export_layer("segments", statement)

    def _export_layer(self, name, statement):
        # Première lettre en majuscule pour le nom du fichier
        capitalized_name = name.capitalize()

        db_params = f"host={CONFIG['database']['host']} " \
                    f"dbname={CONFIG['database']['database']} " \
                    f"user={CONFIG['database']['user']} " \
                    f"password={CONFIG['database']['password']} " \
                    f"port={CONFIG['database']['port']}"

        command = f'ogr2ogr -sql "{statement}" -nln "{name}" ' \
                f'{self.data_dir}/France_{capitalized_name}.geojson "PG:{db_params}"'

        subprocess.check_call(command, shell=True)

    def _push_changes(self):
        # Push to data directory
        push_cmd = f"cd {self.data_dir} && git commit -a -m 'backup' && git push"
        subprocess.run(push_cmd, shell=True, timeout=10)

        # Pull in Dropbox
        pull_cmd = f"cd {self.dropbox} && git pull"
        subprocess.run(pull_cmd, shell=True, timeout=10)

def saveProject():
    try:
        git_handler = GitHandler()
        db_conn = DatabaseConnexion()

        # Vérifie si on est sur la branche backup
        if git_handler.backup_data():
            iface.messageBar().pushMessage(
                "Succès",
                "Couches compositions et segments exportées et poussées sur la branche 'backup'.",
                level=Qgis.Success
            )
        else:
            iface.messageBar().pushMessage(
                "Attention",
                "Les couches n'ont pas été exportées car vous n'êtes pas sur la branche 'backup'. "
                "Utilisez 'git checkout backup'",
                level=Qgis.Warning
            )

    except subprocess.CalledProcessError as e:
        iface.messageBar().pushMessage(
            "Erreur",
            f"Erreur lors de l'exécution de la commande : {str(e)}",
            level=Qgis.Critical
        )
    except subprocess.TimeoutExpired:
        iface.messageBar().pushMessage(
            "Erreur",
            "Timeout lors de l'exécution des commandes git",
            level=Qgis.Critical
        )
    except Exception as e:
        iface.messageBar().pushMessage(
            "Erreur",
            f"Une erreur inattendue s'est produite : {str(e)}",
            level=Qgis.Critical
        )


def openProject():
    try:
        db_conn = DatabaseConnexion()
        qgis_handler = QgisHandler()

        if db_conn.check_column_type() == 'ARRAY':
            db_conn.array_to_text()

        elif db_conn.check_column_type() == 'TEXT':
            db_conn.text_to_array()
            db_conn.array_to_text()

        qgis_handler.remove_layer("compositions")

        new_layer = qgis_handler.create_postgres_layer("compositions")
        if not new_layer:
            return

        # Ajouter la couche compositions au groupe postgres à la positions 3
        qgis_handler.add_layer_to_group(new_layer, "Postgres", 3)

        db_conn.text_to_array()

        qgis_handler.show_attribute_table(new_layer)

    except Exception as e:
        iface.messageBar().pushMessage("Erreur", str(e), level=Qgis.Critical)







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

cur.close()
conn.close()
