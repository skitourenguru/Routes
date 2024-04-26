from qgis.core import *
from qgis.gui import *
from qgis.PyQt.QtWidgets import *
from qgis.analysis import QgsNativeAlgorithms
from qgis.utils import iface
from qgis.core import QgsVectorFileWriter
import psycopg2

######################################################### Reload Compositions layer #############################################################################

# When you reload Qgis, we have to make Qgis believe segments column is text, because it's easier to use, but in the database the column need to be an array.



# Change the variables here
db_name = "Routes"
# group inside which you're compositions and segments layers are inside, in Qgis Legend Interface.
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
root.insertLayer(4, new) # 4 because i have 3 layers upside compositions in my Qgis Legend Interface.
    
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