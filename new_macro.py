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
        'data': '/home/ulysse/Data/Vecteurs/Routes/France',
        'warnings': '/home/ulysse/Data/Vecteurs/Skitourenguru_Public',
        'logs': '/home/ulysse/Code/logs'
    },
    'regex': {
        'no_problems': r"Had no problems",
        'problems': r"Had problems with (\d+) routes",
        'stop_here': r"Created \d+ new routes",
        'capture_that': r"Segment (\d+) is not well connected"
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

    def truncate_alertes(self):
        with self.get_db_connexion() as conn:
            with conn.cursor() as cur:
                cur.execute("TRUNCATE TABLE Alerte;")
                conn.commit()

    def insert_alertes(self, segment_id):
        with self.get_db_connexion() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO Alerte (id, geom)
                    SELECT %s, geom
                    FROM segments
                    WHERE %s = segments.id;
                """, (segment_id, segment_id))
                conn.commit()

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

class QgisHandler:
    def __init__(self):
        self.project = QgsProject.instance()

    def refresh_compositions_layer(self):
        self.db = DatabaseConnexion()
        self.db.array_to_text()

        # Supprimer l'ancienne couche
        if "compositions" in [layer.name() for layer in self.project.mapLayers().values()]:
            layer = self.project.mapLayersByName("compositions")[0]
            self.project.removeMapLayer(layer.id())

        # Créer la nouvelle connexion
        uri = QgsDataSourceUri()
        d = CONFIG['database']
        uri.setConnection(d['host'], str(d['port']), d['database'], d['user'], d['password'])
        uri.setDataSource("public", "compositions", "geom")

        # Ajouter la nouvelle couche
        new_layer = QgsVectorLayer(uri.uri(), "compositions", "postgres")
        if new_layer.isValid():
            root = self.project.layerTreeRoot()
            postgres_group = root.findGroup("Postgres")
            self.project.addMapLayer(new_layer, False)
            postgres_group.insertLayer(3, new_layer)

            # Reconvertir en array et ouvrir la table d'attributs
            self.db.text_to_array()
            iface.showAttributeTable(new_layer)
        else:
            print("Erreur lors du chargement de la couche compositions")

class WarningHandler:
    def __init__(self):
        self.db = DatabaseConnexion()
        self.today = datetime.date.today()

    def find_warnings(self, texte):
        segids = []
        match_arret = re.search(CONFIG['regex']['stop_here'], texte, re.DOTALL)
        if match_arret:
            texte_avant_arret = texte[:match_arret.start()]
            for match in re.finditer(CONFIG['regex']['capture_that'], texte_avant_arret):
                segids.append(match.group(1))
        return segids

    def get_frequence(self, segids):
        return collections.Counter(segids)

    def process_warnings(self):
        try:
            # Télécharger et lire le fichier
            self.download_warnings()
            self.db.truncate_alertes()

            with open(f"{CONFIG['paths']['warnings']}/Warnings.log", "r") as f:
                texte = f.read()

            match_problems = re.search(CONFIG['regex']['problems'], texte)
            nombre_de_problemes = match_problems.group(1) if match_problems else 0

            if re.search(CONFIG['regex']['no_problems'], texte):
                self.show_message("Aucun problème trouvé", "success")
                return

            warnings = self.find_warnings(texte)
            if warnings:
                frequences = self.get_frequence(warnings)
                self.handle_warnings(frequences, nombre_de_problemes)

        except Exception as e:
            self.show_message(f"Erreur: {str(e)}", "critical")

    def download_warnings(self):
        cmd = f"curl https://download.skitourenguru.com/public/Warnings.log --output {CONFIG['paths']['warnings']}/Warnings.log"
        subprocess.run(cmd, shell=True, timeout=15)

    def handle_warnings(self, frequences, nombre_de_problemes):
        with open(f"{CONFIG['paths']['logs']}/Warnings_short.log", "w") as f:
            for segment_id, freq in frequences.items():
                message = self.format_message(segment_id, freq)
                f.write(f'{self.today} : {message}.\n')
                self.db.insert_alertes(segment_id)

        self.show_warning_widget(nombre_de_problemes)

    def show_warning_widget(self, nombre_de_problemes):
        def show_error():
            subprocess.run(["flatpak", "run", "org.gnome.TextEditor",
                          f"{CONFIG['paths']['logs']}/Warnings_short.log"])

        widget = iface.messageBar().createMessage("Warnings",
                                                f"Problème avec {nombre_de_problemes} routes")
        button = QPushButton(widget)
        button.setText("Voir")
        button.pressed.connect(show_error)
        widget.layout().addWidget(button)
        iface.messageBar().pushWidget(widget, Qgis.MessageLevel.Warning)

    @staticmethod
    def format_message(segment_id, freq):
        return (f"Problème avec le segment {segment_id}" +
                (f" dans {freq} itinéraires" if freq > 1 else ""))

    @staticmethod
    def show_message(message, level):
        levels = {
            'info': Qgis.MessageLevel.Info,
            'warning': Qgis.MessageLevel.Warning,
            'critical': Qgis.MessageLevel.Critical,
            'success': Qgis.MessageLevel.Success
        }
        iface.messageBar().pushMessage("Warnings", message,
                                     level=levels[level], duration=6)

def saveProject():
    git_handler = GitHandler()
    if git_handler.backup_data():
        iface.messageBar().pushMessage(
            "Sauvegarde réussie",
            "Couches compositions et segments exportées et poussées sur la branche 'backup'",
            level=Qgis.MessageLevel.Success
        )
    else:
        iface.messageBar().pushMessage(
            "Erreur de sauvegarde",
            "Vous n'êtes pas sur la branche 'backup'. Utilisez 'git checkout backup'",
            level=Qgis.MessageLevel.Warning
        )

def openProject():
    try:
        qgis_handler = QgisHandler()
        warning_handler = WarningHandler()

        # Mise à jour de la couche compositions
        qgis_handler.refresh_compositions_layer()

        # Traitement des warnings
        warning_handler.process_warnings()

    except Exception as e:
        iface.messageBar().pushMessage(
            "Erreur",
            str(e),
            level=Qgis.MessageLevel.Critical
        )
