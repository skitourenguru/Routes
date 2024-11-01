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

# You only have to change the CONFIG below, and normally, just to change the database name and the group name.

CONFIG = {
    'database': {
        'host': 'localhost',
        'database': 'France_Alpes',
        'user': 'postgres',
        'password': 'postgres',
        'port': 5432
    },
    'group': 'Postgres'
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
        qgis_handler.add_layer_to_group(new_layer, CONFIG['group'], 3)

        db_conn.text_to_array()

        qgis_handler.show_attribute_table(new_layer)

    except Exception as e:
        iface.messageBar().pushMessage("Erreur", str(e), level=Qgis.Critical)
