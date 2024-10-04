"""
Permet de supprimer un segment dans la colonne segments de la table compositions.
"""

import psycopg2

# Choisir le segment à supprimer
segment_a_supprimer = 0

#Choisir le segment à la droite de celui à supprimer
pour_tous_les_itineraires_comportant_le_segment = 0

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="test",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

cur.execute(f"""
    UPDATE compositions
    SET segments = array_remove(segments, {segment_a_supprimer})
    WHERE {pour_tous_les_itineraires_comportant_le_segment} = ANY(segments);
""")
print(f"Vous avez supprimé le segment {segment_a_supprimer}, pour tous les itinéraires comportant le segment {pour_tous_les_itineraires_comportant_le_segment}")

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
