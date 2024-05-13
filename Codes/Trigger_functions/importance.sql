CREATE or REPLACE FUNCTION importance() RETURNS TRIGGER AS $$
BEGIN

IF (TG_OP = 'UPDATE') Then

UPDATE segments 
SET importance = compositions.importance
FROM compositions, unnest(segments) AS segid
WHERE segid = segments.id;

END IF;
RETURN NEW;

END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER importance
AFTER UPDATE OF importance
ON compositions
FOR EACH ROW
EXECUTE FUNCTION importance();