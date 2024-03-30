import psycopg2
import json
from pygit2 import Repository
from qgis.utils import iface

dossier = '/home/ulysse/Dropbox/skitourenguru/Routes'
repo = Repository(dossier)
head = repo.head.name

if head == "refs/heads/main":
    try:
        conn = psycopg2.connect(
            dbname="France_Alpes",
            user="postgres",
            password="postgres",
            host="localhost"
        )

        cur = conn.cursor()
        cur.execute("ALTER TABLE compositions ALTER segments TYPE TEXT USING array_to_string(segments, ',');")


        cur = conn.cursor()
        cur.execute("SELECT id, start, stop, routes, mdiff, importance, segments FROM compositions ORDER BY id")

        columns = cur.fetchall()
        features = []

        for column in columns:
            feature = {
                "type": "Feature",
                "properties": {
                    "id": column[0],
                    "start": column[1],
                    "stop": column[2],
                    "routes": column[3],
                    "mdiff": column[4],
                    "importance": column[5],
                    "segments": column[6]
                }
            }
            features.append(feature)

        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }
        with open(f'{dossier}/France/France_Compositions.geojson', 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f)
        print("GeoJSON exporté avec succès dans /Routes/France")

        cur = conn.cursor()
        cur.execute("SELECT fid, id, importance, st_asGeojson(geom) FROM segments ORDER BY id")

        columns = cur.fetchall()
        features = []

        for column in columns:
            try:
                feature = {
                    "type": "Feature",
                    "geometry": json.loads(column[3]),
                    "properties": {
                        "fid": column[0],
                        "id": column[1],
                        "importance": column[2]
                    }
                }
                features.append(feature)
            except json.JSONDecodeError as e:
                print("Erreur lors du chargement du JSON:", e)

        geojson_data = {
            "type": "FeatureCollection",
            "features": features
        }
        with open(f'{dossier}/France/France_Segments.geojson', 'w', encoding='utf-8') as f:
            json.dump(geojson_data, f)
        print("GeoJSON exporté avec succès dans /Routes/France")

    except psycopg2.Error as e:
        print("Erreur lors de la connexion à la base de données:", e)

    finally:
        if conn is not None:
            conn.close()
else:
    iface.messageBar().pushMessage("Layers Segments & Compositions not exported because you're on Backup branch. Please switch to Main : 'git checkout main' ")