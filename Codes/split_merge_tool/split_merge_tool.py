from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QTimer, QSettings
from qgis.core import QgsApplication, QgsProject
import os.path
from .Qgis_split_and_merge import show_dialog, start_script, stop_script

class SplitMergeTool:
    def __init__(self, iface):
        self.iface = iface
        self.dialog = None
        self.actions = []
        self.menu = 'Split & Merge Tool'
        self.toolbar = self.iface.addToolBar('Split & Merge')
        self.toolbar.setObjectName('SplitMergeToolbar')


    def initGui(self):
        """Crée les actions et ajoute les boutons à la barre d'outils"""
        icon_path = os.path.join(os.path.dirname(__file__), 'icons', 'icon.png')
        show_action = QAction(
            QIcon(icon_path),
            'Ouvrir Split & Merge',
            self.iface.mainWindow()
        )
        show_action.triggered.connect(self.show_dialog)
        self.toolbar.addAction(show_action)
        self.actions.append(show_action)

    def on_project_load(self):
        """Fonction appelée quand un projet est chargé"""
        self.project_loaded = True
        if self.auto_start and not hasattr(self, 'dialog') or not self.dialog or not self.dialog.script_running:
            QTimer.singleShot(1000, self.check_and_start)


    def check_and_start(self):
        """Vérifie si les couches nécessaires sont présentes avant de démarrer"""
        if not self.auto_start or not self.project_loaded:
            return

        project = QgsProject.instance()
        if not project:
            return

        settings = QSettings()
        segments_layer = settings.value("split_merge/segments_layer", "segments")
        compositions_layer = settings.value("split_merge/compositions_layer", "compositions")

        segments_layers = project.mapLayersByName(segments_layer)
        compositions_layers = project.mapLayersByName(compositions_layer)

        if segments_layers and compositions_layers:
            self.quick_start()
        else:
            self.iface.messageBar().pushWarning(
                "Split & Merge",
                f"Les couches requises ({segments_layer} et {compositions_layer}) n'ont pas été trouvées"
            )

    def unload(self):
        """Supprime les éléments de l'interface"""
        for action in self.actions:
            self.iface.removeToolBarIcon(action)
            self.iface.removePluginMenu(self.menu, action)
        if self.dialog:
            self.dialog.close()
        del self.toolbar

    def show_dialog(self):
        """Affiche la fenêtre de dialogue"""
        if self.dialog is None:
            self.dialog = show_dialog()
        self.dialog.show()
        self.dialog.activateWindow()

    def quick_start(self):
        """Démarre directement le script sans afficher l'interface"""
        try:
            # Ne démarrer que si le script n'est pas déjà en cours d'exécution
            if not hasattr(self, 'dialog') or not self.dialog or not self.dialog.script_running:
                success = start_script()
                if success:
                    self.auto_start = True  # Maintenir l'auto-start actif
                    if self.dialog:
                        self.dialog.script_running = True
                        self.dialog.update_ui_state()  # Mettre à jour l'interface si elle existe
                    self.iface.messageBar().pushSuccess(
                        "Split & Merge",
                        "Script démarré automatiquement"
                    )
        except Exception as e:
            self.iface.messageBar().pushCritical(
                "Split & Merge",
                f"Erreur au démarrage: {str(e)}"
            )
