from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFeature,
    Qgis,
    QgsFeatureRequest,
    QgsWkbTypes,
    QgsSpatialIndex
)
from qgis.utils import iface
from typing import Literal, Optional, cast
from PyQt5.QtCore import QTimer
import time
from functools import wraps

last_fid = 0

def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} a pris {(end - start)*1000:.2f} ms")
        return result
    return wrapper

def get_features_list(layer, request=None):
    features = []
    if request:
        iterator = layer.getFeatures(request)
    else:
        iterator = layer.getFeatures()

    feature = next(iterator, None)
    while feature:
        features.append(feature)
        feature = next(iterator, None)
    return features

@timer_decorator
def feature_added(fid):

    # Empêche Qgis de planter. Sûrement une histoire de priorité de tâche. J'ai trouvé ça pour y parer.'
    QTimer.singleShot(1, lambda: process_new_feature(fid))

@timer_decorator
def process_new_feature(fid):
    """
    Traite une nouvelle feature ajoutée
    """
    global last_fid

    if last_fid == fid:
        return

    print(f"\n{'='*50}")
    print(f"Traitement nouvelle entité FID={fid}")
    print(f"{'='*50}")

    source_feature = segments_layer.getFeature(fid)
    if not source_feature.fields().names():
        print("ERREUR: Pas de champs dans la feature source")
        return

    id_idx = source_feature.fields().indexOf('id')
    segment_id = source_feature.attributes()[id_idx]

    print(f"ID du segment: {segment_id}")

    if segment_id and has_duplicate_segment_id(segment_id):
        print(f"Segment {segment_id} détecté comme dupliqué")

        new_geometry = source_feature.geometry()
        if not new_geometry or new_geometry.isEmpty():
            print("ERREUR: Géométrie invalide pour le nouveau segment")
            return

        # Récupérer le segment original
        expression = f"\"id\" = '{segment_id}' AND $id != {fid}"
        request = QgsFeatureRequest().setFilterExpression(expression)
        original_feature = next(segments_layer.getFeatures(request), None)

        if original_feature:
            print(f"Segment original trouvé: FID={original_feature.id()}")

            # Vérifier les géométries
            print_geometry_info(original_feature.geometry(), "Segment original")
            print_geometry_info(new_geometry, "Nouveau segment")

            # Récupérer toutes les compositions contenant ce segment
            segment_lists = get_compositions_list_segments(segment_id)
            print(f"Nombre de compositions trouvées: {len(segment_lists)}")

            if segment_lists:
                next_id = get_next_id()
                print(f"Nouvel ID à attribuer: {next_id}")

                # Mettre à jour les compositions
                update_compositions_segments(segment_id, next_id, original_feature, source_feature, segment_lists)

                # Mettre à jour l'ID du nouveau segment
                update_segment_id(fid, next_id)
            else:
                print("ATTENTION: Aucune composition trouvée pour ce segment")
        else:
            print("ERREUR: Segment original non trouvé")
    else:
        print("Le segment n'est pas un duplicata ou n'a pas d'ID valide")

    last_fid = fid
    clean_invalid_segments()

def print_geometry_info(geometry, label):
    """Affiche les informations détaillées sur une géométrie"""
    if not geometry or geometry.isEmpty():
        print(f"{label}: Géométrie invalide ou vide")
        return

    points = geometry.asPolyline()
    print(f"""
    {label}:
    - Type: {geometry.wkbType()}
    - Longueur: {geometry.length():.2f}
    - Nombre de points: {len(points)}
    - Premier point: {points[0]}
    - Dernier point: {points[-1]}
    """)

@timer_decorator
def get_compositions_list_segments(segment_id):
    """
    Récupère toutes les listes de segments contenant l'id du segment divisé
    """
    if not segment_id:
        return []

    all_segments_lists = []

    print(f"\nRecherche du segment {segment_id} dans les compositions")

    request = QgsFeatureRequest()
    expression = f"segments LIKE '%,{segment_id},%' OR segments LIKE '{segment_id},%' OR segments LIKE '%,{segment_id}' OR segments = '{segment_id}'"
    request.setFilterExpression(expression)

    features = get_features_list(compositions_layer, request)

    print(f"Nombre de compositions trouvées avec la requête: {len(features)}")

    for feature in features:
        segments_str = feature['segments']
        print(f"\nExamen de la composition {feature.id()}:")
        print(f"Liste brute: {segments_str}")

        if not segments_str:
            print("Liste vide, ignorée")
            continue

        try:
            segments_ids = [int(id.strip()) for id in str(segments_str).split(',')]
            print(f"Liste convertie: {segments_ids}")

            if int(segment_id) in segments_ids:
                print(f"Segment {segment_id} trouvé dans la composition {feature.id()}")
                all_segments_lists.append(segments_ids)
            else:
                print(f"Segment {segment_id} non trouvé dans cette liste")

        except Exception as e:
            print(f"Erreur lors du traitement de la composition {feature.id()}: {str(e)}")

    print(f"\nNombre total de listes trouvées: {len(all_segments_lists)}")
    return all_segments_lists

@timer_decorator
def update_compositions_segments(old_id, new_id, original_feature, new_feature, segment_lists):
    """
    Met à jour les compositions après division d'un segment
    """
    print(f"\nMise à jour des compositions:")
    print(f"- Ancien ID: {old_id}")
    print(f"- Nouvel ID: {new_id}")

    compositions_layer.startEditing()

    original_geom = original_feature.geometry()
    new_geom = new_feature.geometry()

    for segments_list in segment_lists:
        print(f"\nTraitement liste: {segments_list}")
        try:
            old_index = segments_list.index(int(old_id))
            print(f"Position du segment dans la liste: {old_index}")

            # Vérifier l'orientation
            prev_geom = segments_layer.getFeature(segments_list[old_index - 1]).geometry() if old_index > 0 else None
            next_geom = segments_layer.getFeature(segments_list[old_index + 1]).geometry() if old_index < len(segments_list) - 1 else None

            is_correctly_oriented = check_segment_orientation(
                original_geom if old_index > 0 else new_geom,
                prev_geom,
                next_geom
            )
            print(f"Orientation correcte: {is_correctly_oriented}")

            new_segments_list = segments_list.copy()

            if is_correctly_oriented:
                new_segments_list[old_index:old_index+1] = [int(old_id), int(new_id)]
            else:
                new_segments_list[old_index:old_index+1] = [int(new_id), int(old_id)]

            print(f"Nouvelle liste: {new_segments_list}")

            # Mettre à jour la composition
            request = QgsFeatureRequest().setFilterExpression(f"segments = '{','.join(map(str, segments_list))}'")
            composition_feature = next(compositions_layer.getFeatures(request), None)

            if composition_feature:
                result = compositions_layer.changeAttributeValue(
                    composition_feature.id(),
                    compositions_layer.fields().indexOf('segments'),
                    ','.join(map(str, new_segments_list))
                )
                print(f"Mise à jour réussie: {result}")
            else:
                print("ERREUR: Composition non trouvée")

        except Exception as e:
            print(f"ERREUR lors de la mise à jour: {str(e)}")

@timer_decorator
def clean_invalid_segments() -> None:
    """
    Supprime les références aux segments qui n'existent plus dans la table segments
    """
    valid_segments_ids = {str(f['id']) for f in get_features_list(segments_layer) if f['id'] is not None}
    compositions = get_features_list(compositions_layer)

    compositions_layer.startEditing()
    for composition in compositions:
        segments_str = composition['segments']
        if segments_str is None or str(segments_str).upper() == 'NULL' or not segments_str:
            continue

        segments_list = str(segments_str).split(',')
        valid_segments = [seg.strip() for seg in segments_list if seg.strip() in valid_segments_ids]

        if len(valid_segments) != len(segments_list):
            new_segments_str = ','.join(valid_segments)
            compositions_layer.changeAttributeValue(
                composition.id(),
                composition.fields().indexOf('segments'),
                new_segments_str
            )

@timer_decorator
def has_duplicate_segment_id(segment_id: str) -> bool:
    """
    Vérifie si un id de segments existe plusieurs fois. Si oui, il s'agit d'un segment divisé.
    Args:
    """

    expression = f"\"id\" = '{segment_id}'"
    request = QgsFeatureRequest().setFilterExpression(expression)
    request.setLimit(2)

    features = get_features_list(segments_layer, request)
    return len(features) > 1

@timer_decorator
def update_segment_id(fid, next_id):
    """
    Met à jour l'id des segments divisés.
    """
    segments_layer.startEditing()
    segments_layer.changeAttributeValue(fid,
        segments_layer.fields().indexOf('id'),
        str(next_id))

@timer_decorator
def get_next_id():

    next_id = int(segments_layer.maximumValue(segments_layer.fields().indexOf('id')))
    return next_id + 1

@timer_decorator
def check_segment_orientation(segment_geom, prev_segment_geom=None, next_segment_geom=None):
    """
    Vérifie si un segment est orienté correctement par rapport aux segments adjacents.
    """
    if segment_geom.isEmpty():
        return True

    segment_points = segment_geom.asPolyline()

    # Vérifier avec le segment précédent
    if prev_segment_geom and not prev_segment_geom.isEmpty():
        prev_points = prev_segment_geom.asPolyline()
        if prev_points[-1].distance(segment_points[0]) > prev_points[-1].distance(segment_points[-1]):
            return False

    # Vérifier avec le segment suivant
    if next_segment_geom and not next_segment_geom.isEmpty():
        next_points = next_segment_geom.asPolyline()
        if segment_points[-1].distance(next_points[0]) > segment_points[0].distance(next_points[0]):
            return False

    return True

def update_compositions_geometry():
    """
    Met à jour la géométrie des compositions en fusionnant les géométries des segments associés
    """
    # print("update_compositions_geometry")
    # compositions_layer.startEditing()
    # compositions = get_features_list(compositions_layer)

    # for composition in compositions:  # Utiliser composition au lieu de feature
    #     segments_str = composition['segments']

    # # Skip si pas de segments
    # if not segments_str or str(segments_str).upper() == 'NULL':
    #     continue

    # # Obtenir la liste des IDs des segments
    # segments_ids = [int(id.strip()) for id in str(segments_str).split(',')]

    # # Collecter toutes les géométries des segments associés
    # collected_geom = None
    # for segment_id in segments_ids:
    #     # Récupérer le segment
    #     expression = f"\"id\" = '{segment_id}'"
    #     request = QgsFeatureRequest().setFilterExpression(expression)
    #     segment_features = segments_layer.getFeatures(request)

    #     # Prendre le premier (et normalement unique) segment correspondant
    #     segment = next(segment_features, None)
    #     if segment:
    #         if collected_geom is None:
    #             collected_geom = segment.geometry()
    #         else:
    #             collected_geom = collected_geom.combine(segment.geometry())

    # # Mettre à jour la géométrie de la composition
    # if collected_geom:
    #     composition.setGeometry(collected_geom)
    #     compositions_layer.updateFeature(composition)

@timer_decorator
def start_script():
    global segments_layer, compositions_layer, id_field_index, segments_field_index

    project = QgsProject.instance()
    if not project:
        return

    segments_layers = project.mapLayersByName('segments')
    compositions_layers = project.mapLayersByName('compositions')


    if segments_layers and compositions_layers:
        segments_layer = cast(QgsVectorLayer, segments_layers[0])
        compositions_layer = cast(QgsVectorLayer, compositions_layers[0])


    if isinstance(segments_layer, QgsVectorLayer) and isinstance(compositions_layer, QgsVectorLayer):

        # segments_index = QgsSpatialIndex(segments_layer.getFeatures())
        # compositions_index = QgsSpatialIndex(compositions_layer.getFeatures())

        id_field_index = segments_layer.fields().indexOf('id')
        segments_field_index = compositions_layer.fields().indexOf('segments')

        segments_layer.featureAdded.connect(feature_added)
        iface.messageBar().pushMessage("Info", "Script démarré", level=Qgis.MessageLevel.Info)

def stop_script():

    try:
        segments_layer.featureAdded.disconnect(feature_added)
        iface.messageBar().pushMessage("Info", "Script arrêté", level=Qgis.MessageLevel.Info)
    except:
        pass
