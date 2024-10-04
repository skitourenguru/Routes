"""
Permet d'inserer un segment dans la colonne segments de la table compositions.
"""

import psycopg2

# Où insérer un segment ?
Au_debut = 0
Au_milieu = 0
A_la_fin = 0

# Quel segment insérer ?
segment_a_insere = 0

# Entre quels segments insérer ?

segment_de_gauche = 0        # S'il s'agit du dernier segment, n'entrez que celui-ci
segment_de_droite = 0        # S'il s'agit du premier segment, n'entrez que celui-ci

# Connect to the database
conn = psycopg2.connect(
    host="localhost",
    database="test",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()

if Au_debut == 1:

    cur.execute(f"""
        UPDATE compositions
        SET segments = array_prepend({segment_a_insere}, segments)
        WHERE {segment_de_droite} = ANY(segments);
    """)
    print(f"Les itinéraires commençant par le segment {segment_de_droite}, commencent désormais par le segment {segment_a_insere}")

elif Au_milieu == 1:

    cur.execute(f"""
        UPDATE compositions
        SET segments = segments[:array_position(segments, {segment_de_gauche})] || {segment_a_insere} || segments[array_position(segments, {segment_de_gauche})+1:]
        WHERE {segment_de_droite} = ANY(segments);
    """)
    print(f'Vous avez inséré le segment {segment_a_insere} entre le segment {segment_de_gauche} et le segment {segment_de_droite}.')

elif A_la_fin == 1:

    cur.execute(f"""
        UPDATE compositions
        SET segments = array_append(segments, {segment_a_insere})
        WHERE {segment_de_gauche} = ANY(segments);
    """)
    print(f"Les itinéraires se terminant par le {segment_de_gauche}, terminent désormais par le segment {segment_a_insere}")

else:
    print("Vous devez choisir la place du segment à insérer.")

# Commit the transaction
conn.commit()

# Close the cursor and connection
cur.close()
conn.close()
