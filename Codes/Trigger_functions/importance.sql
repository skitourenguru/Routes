CREATE or REPLACE FUNCTION importance() RETURNS TRIGGER AS $$
BEGIN

IF (TG_OP = 'UPDATE') Then

UPDATE segments
SET importance = 0;

WITH
a AS (
	SELECT 	unnest(segments) AS id,
	 		importance 
	FROM 	compositions 
	WHERE 	importance = 0),  
b AS (
	SELECT 	unnest(segments) AS id,
			importance 
	FROM	compositions 
	WHERE 	importance = 1
	),
d AS (
	SELECT 	unnest(segments) AS id,
			importance 
	FROM 	compositions 
	WHERE 	importance = 2
	),
c AS (
	SELECT 	b.id,
			b.importance 
	FROM 	b 
	WHERE 	b.id NOT IN (SELECT a.id FROM a) 
	UNION
	SELECT 	d.id, 
			d.importance 
	FROM 	d 
	WHERE 	d.id NOT IN (SELECT a.id FROM a)
	)

UPDATE segments 
SET importance = c.importance
FROM c
WHERE c.id = segments.id;


END IF;
RETURN NEW;

END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER importance
AFTER UPDATE OF importance
ON compositions
FOR EACH ROW
EXECUTE FUNCTION importance();