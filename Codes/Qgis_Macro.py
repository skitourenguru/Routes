from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.utils import iface
from qgis.core import QgsVectorFileWriter
import psycopg2

######################################################### Reload Compositions layer #############################################################################
db_name = "Routes"
group = "PostGis"


#Get connexion to the Database
conn = psycopg2.connect(
    host = "localhost",
    database = db_name,
    user = "postgres",
    password = "postgres"
)

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
uri.setConnection("localhost", "5432", db_name, "postgres", "postgres")
uri.setDataSource("public", "compositions", "geom")

# Find the place where to insert the new compositions layer
root = QgsProject.instance().layerTreeRoot()
root = root.findGroup(group) 
# And Insert it
new = QgsVectorLayer(uri.uri(), "compositions", "postgres")
QgsProject.instance().addMapLayer(new, False)
root.insertLayer(4, new)
    
# Change again the type, String to Array.

cur = conn.cursor()
cur.execute("""
      ALTER TABLE compositions 
            ALTER segments TYPE INTEGER[] USING string_to_array(segments, ',')::int[]
""")
conn.commit()

# Open the attribute table from Compositions.
layer = QgsProject.instance().mapLayersByName('compositions')[0]
iface.showAttributeTable(layer)