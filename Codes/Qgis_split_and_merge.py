from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    Qgis,
    QgsFeatureRequest
)
from qgis.utils import iface
from typing import Literal, Optional
from PyQt5.QtCore import QTimer


def feature_added(fid):
    # Empêche Qgis de planter. Sûrement une histoire de priorité de tâche. J'ai trouvé ça pour y parer.'
    QTimer.singleShot(1, lambda: process_new_feature(fid))

def process_new_feature(fid):
    """
    Fonction principale, appelée quand une nouvelle entité est ajoutée à la couche segments.
    Args:
        fid: L'identifiant de l'entité qui vient d'être ajoutée
    """
    source_feature = segments_layer.getFeature(fid)
    if not source_feature.fields().names():
            return

    # Méthode détournée pour accéder à l'id, il y a un bug de Qgis qui soulève une KeyError autrement.'
    id_idx = source_feature.fields().indexOf('id')
    segment_id = source_feature.attributes()[id_idx]

        # Vérifier si c'est un segment divisé.
    if segment_id and has_duplicate_segment_id(segment_id):
        update_segments_list(segment_id)
        # Puis mettre à jour l'id.
        update_segment_id(fid)
    else:
        clean_invalid_segments()

def update_segments_list(segment_id):
    if segment_id:
        compositions_ids = []

        for feature in compositions_layer.getFeatures():
            segments_list = feature['segments']
            if segments_list:
                segments_ids = [int(id.strip()) for id in str(segments_list).split(',')]
                if segment_id in segments_ids:
                    compositions_ids.append(feature.id())
                    index = segments_ids.index(segment_id)
                    last_id = get_next_id(segments_layer)
                    segments_ids.insert(index + 1, last_id)
                    new_list = ','.join(map(str, segments_ids))

                    compositions_layer.startEditing()
                    compositions_layer.changeAttributeValue(feature.id(), feature.fields().indexOf('segments'), new_list)

        if compositions_ids:
            return

def clean_invalid_segments() -> None:
    """
    Supprime les références aux segments qui n'existent plus dans la table segments
    """
    # Récupère tous les IDs valides de la table segments
    valid_segments_ids = [str(f['id']) for f in segments_layer.getFeatures() if f['id'] is not None]

    # Pour chaque composition
    compositions_layer.startEditing()
    for composition in compositions_layer.getFeatures():
        segments_str = composition['segments']

        # Skip si NULL ou vide
        if segments_str is None or str(segments_str).upper() == 'NULL' or not segments_str:
            continue

        # Convertit la chaîne en liste
        segments_list = str(segments_str).split(',')

        # Garde uniquement les segments qui existent dans la table segments
        valid_segments = [seg.strip() for seg in segments_list if seg.strip() in valid_segments_ids]

        # Si des segments ont été supprimés, met à jour la composition
        if len(valid_segments) != len(segments_list):
            new_segments_str = ','.join(valid_segments)
            compositions_layer.changeAttributeValue(
                composition.id(),
                composition.fields().indexOf('segments'),
                new_segments_str
            )

def has_duplicate_segment_id(segment_id: str) -> bool:
    """
    Vérifie si un id de segments existe plusieurs fois. Si oui, il s'agit d'un segment divisé.
    Args:
        segment_id: l'id correspondant à l'entité venant d'être ajoutée
    """

    expression = f"\"id\" = '{segment_id}'"
    request = QgsFeatureRequest().setFilterExpression(expression)
    matching_features = segments_layer.getFeatures(request)
    return sum(1 for _ in matching_features) > 1

def update_segment_id(fid):

    segments_layer.startEditing()
    next_id = get_next_id(segments_layer)
    segments_layer.changeAttributeValue(fid,
                                        segments_layer.fields().indexOf('id'),
                                        str(next_id))

def get_next_id(layer):
    """
    Récupère le prochain id disponible dans la couche
    """
    max_id = int(segments_layer.maximumValue(segments_layer.fields().indexOf('id')))

    return max_id + 1

def start_script():
    global segments_layer, compositions_layer

    # Récupérer les couches
    segments_layers = QgsProject.instance().mapLayersByName('segments')
    compositions_layers = QgsProject.instance().mapLayersByName('compositions')


    segments_layer = segments_layers[0]
    compositions_layer = compositions_layers[0]

    segments_layer.featureAdded.connect(feature_added)
    iface.messageBar().pushMessage("Info", "Script démarré", level=Qgis.MessageLevel.Info)

def stop_script():
    try:
        segments_layer.featureAdded.disconnect(feature_added)
        iface.messageBar().pushMessage("Info", "Script arrêté", level=Qgis.Info)
    except:
        pass
