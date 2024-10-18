# 1. Ajouter un segment dans un tableau

## Ajouter un segment au début d'un tableau

```sql
UPDATE compositions
SET segments = array_prepend(1981, segments)
WHERE 1980 = ANY(segments)
```

/* In this example, segment 1981 is add at all routes where segment 989 is present */

## Ajouter un segment au milieu d'un tableau

```sql
UPDATE compositions
SET segments = segments[:array_position(segments, 3267)]  -- id at the left of the new segment.
    ||3269||                                          -- id of the new segment.
    segments[array_position(segments, 3267)+1:]       -- id at the left of the new segment.
WHERE 3279 = ANY(segments)   				  -- id at the right of the new segment.
```

/*In this example, segment 3269 is insert between segment 3267 and 3279 */

## Ajouter un segment à la fin d'un tableau

```sql
UPDATE compositions
SET segments = array_append(segments, 3400)
WHERE 972 = ANY(segments)
```

/* In this example, segment 3400 is add at all routes where segment 972 is present */

## Supprimer un segment

```sql
UPDATE compositions
SET segments = array_remove(segments, 3269)
WHERE 3265 = ANY(segments)
```

/* In this example, segment 3269 is delete in all routes where segment 3265 is present */

# 2. Changer le type de la colonne segments de la table de compositions

## Text to Array

```sql
ALTER TABLE compositions
ALTER segments TYPE INTEGER[] USING string_to_array(segments, ',')::int[];
```

## Array to Text

```sql
ALTER TABLE compositions
ALTER segments TYPE TEXT USING array_to_string(segments, ',');
```

## Text to Integer

```sql
ALTER TABLE districts
ALTER COLUMN id TYPE INTEGER USING id::integer;
```

# 3. Définir le massif

```sql
WITH
    a AS(SELECT geometry FROM districts WHERE id = 3),
    b AS (SELECT id FROM compositions
        JOIN a ON st_contains(a.geometry,compositions.geom)
        WHERE massif IS NULL)

UPDATE compositions
SET massif = 'Mont-Blanc'
    FROM b
    WHERE compositions.id = b.id
```

# 4. Supprimer les géométries dupliquées

```sql
DELETE FROM merged a
USING
    (SELECT MIN(fid) AS min_fid, geom
    FROM merged
    GROUP BY geom
    HAVING COUNT(*)>1 ) b
WHERE a.fid <> b.min_fid AND st_equals(a.geom, b.geom)
```

# 5. Renouveller à partir des sauvegardes les données de Postgresql

## Vider les tables existantes :

```sql
TRUNCATE TABLE compositions, segments;
```

## Désactiver les déclencheurs :

```sql
ALTER TABLE compositions
DISABLE TRIGGER ALL;

ALTER TABLE segments
DISABLE TRIGGER ALL;
```

## Transformer le type des données :

```sql
ALTER TABLE compositions
ALTER segments TYPE TEXT USING array_to_string(segments, ',');
```

Copier les données sauvegarder vers la base de données :

```bash
ogr2ogr -f PostgreSQL "PG:user=postgres password=postgres dbname=test" /home/ulysse/Dropbox/skitourenguru/Ski-Routes/France-Alpes/France_Alpes_Compositions.geojson && ogr2ogr -f PostgreSQL "PG:user=postgres password=postgres dbname=test" /home/ulysse/Dropbox/skitourenguru/Ski-Routes/France-Alpes/France_Alpes_Segments.geojson
```

## Réactiver les triggers

```sql
ALTER TABLE compositions
ENABLE TRIGGER ALL;

ALTER TABLE segments
ENABLE TRIGGER ALL;
```

## Transformer le type de données à nouveau :

```sql
ALTER TABLE compositions
ALTER segments TYPE INTEGER[] USING string_to_array(segments, ',')::int[];
```

## Réinsérer, une première fois, les géométries dans la table de compositions :

```sql
WITH
    a AS (SELECT compositions.id, st_collect(segments.geom) AS geom
        FROM compositions, UNNEST(segments) AS iti
        JOIN segments ON segments.id = iti
        GROUP BY compositions.id)

UPDATE compositions
SET geom = a.geom
FROM a
WHERE a.id = compositions.id;
```
