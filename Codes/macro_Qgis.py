from pygit2 import Repository
from qgis.utils import iface
from qgis.core import Qgis
import subprocess
import os


CONFIG = {
    "paths": {
        "dropbox": "/home/ulysse/Dropbox/skitourenguru/Routes/France",
        "dossier": "/home/ulysse/Data/Vecteurs/Routes/France",
        "working_dir": "/home/ulysse/Data/Vecteurs/Routes/Working_dir",
    },
    "names": {
        "comp": "compositions",
        "seg": "segments",
        "db": "France_Alpes",
    },
}


class GitHandler:
    def __init__(self):
        self.dropbox = CONFIG["paths"]["dropbox"]
        self.data_dir = CONFIG["paths"]["dossier"]
        self.working_dir = CONFIG["paths"]["working_dir"]
        self.repo = Repository(self.data_dir)

    def backup_data(self):
        if self.repo.head.name == "refs/heads/backup":
            self._export_compositions()
            self._export_segments()
            self._push_changes()
            return True
        return False

    def _export_compositions(self):
        layer_name = CONFIG["names"]["comp"]

        statement = f"""SELECT id, start, stop, routes, mdiff, importance, segments, massif FROM {layer_name} ORDER BY id"""
        self._export_layer(layer_name, statement)

    def _export_segments(self):
        layer_name = CONFIG["names"]["seg"]

        statement = f"""SELECT fid, id, importance, massif, geom FROM {layer_name} ORDER BY id"""
        self._export_layer(layer_name, statement)

    def _export_layer(self, name, statement):
        capitalized_name = name.capitalize()
        geojson_file_path = os.path.join(
            self.data_dir, f"France_{capitalized_name}.geojson"
        )
        if os.path.exists(geojson_file_path):
            os.remove(geojson_file_path)

        db = CONFIG["names"]["db"]

        command = (
            f'ogr2ogr -sql "{statement}" -nln "{name}" '
            f'"{self.data_dir}/France_{capitalized_name}.geojson" '
            f'"{self.working_dir}/{db}.gpkg" '
        )

        try:
            subprocess.check_call(command, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Command failed: {command}")
            print(f"Return code: {e.returncode}")
            raise

    def _push_changes(self):
        try:
            os.chdir("/home/ulysse/Data/Vecteurs/Routes")

            subprocess.run(["git", "add", "."], check=True)

            subprocess.run(["git", "commit", "-m", "backup"], check=True)

            subprocess.run(["git", "push"], check=True)

        except subprocess.CalledProcessError as e:
            print(f"Git command failed: {e.cmd}")
            print(f"Return code: {e.returncode}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            raise

        try:
            os.chdir("/home/ulysse/Dropbox/skitourenguru/Routes")
            subprocess.run(["git", "pull"], check=True)

        except subprocess.CalledProcessError as e:
            print(f"Git pull command failed: {e.cmd}")
            print(f"Return code: {e.returncode}")
            raise


def saveProject():
    try:
        git_handler = GitHandler()

        if git_handler.backup_data():
            iface.messageBar().pushMessage(
                "Succès",
                "Couches compositions et segments exportées et poussées sur la branche 'backup'.",
                level=Qgis.MessageLevel.Success,
            )
        else:
            iface.messageBar().pushMessage(
                "Attention",
                "Les couches n'ont pas été exportées car vous n'êtes pas sur la branche 'backup'. "
                "Utilisez 'git checkout backup'",
                level=Qgis.MessageLevel.Warning,
            )

    except subprocess.CalledProcessError as e:
        iface.messageBar().pushMessage(
            "Erreur",
            f"Erreur lors de l'exécution de la commande : {str(e)}",
            level=Qgis.MessageLevel.Critical,
        )
    except subprocess.TimeoutExpired:
        iface.messageBar().pushMessage(
            "Erreur",
            "Timeout lors de l'exécution des commandes git",
            level=Qgis.MessageLevel.Critical,
        )
    except Exception as e:
        iface.messageBar().pushMessage(
            "Erreur",
            f"Une erreur inattendue s'est produite : {str(e)}",
            level=Qgis.MessageLevel.Critical,
        )


if __name__ == "__main__":
    saveProject()
