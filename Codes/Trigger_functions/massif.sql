CREATE or REPLACE FUNCTION set_massif() RETURNS TRIGGER AS $$
BEGIN

IF (TG_OP = 'UPDATE') Then

WITH 
compo_list AS
(SELECT segid, massif 
FROM compositions, UNNEST(segments) AS segid),

new_massif AS
(SELECT segments.id AS id, compo_list.massif AS massif
FROM compo_list 
JOIN segments ON compo_list.segid = segments.id
WHERE segments.massif IS NULL)

UPDATE segments
SET massif = new_massif.massif
FROM new_massif
WHERE new_massif.id = segments.id;

END IF;
RETURN NEW;

END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER massif_update
AFTER UPDATE OF massif
ON compositions
FOR EACH ROW
EXECUTE FUNCTION set_massif();