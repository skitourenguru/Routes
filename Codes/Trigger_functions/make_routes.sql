CREATE or REPLACE FUNCTION make_routes() RETURNS TRIGGER AS $$

BEGIN

/* The compositions table must have a geometry column. Default name "geom".  */

IF (TG_OP = 'INSERT') or (TG_OP = 'UPDATE') or (TG_OP = 'DELETE')  THEN

	WITH
    a AS (SELECT compositions.id, st_collect(segments.geom) AS geom
		FROM compositions, UNNEST(segments) AS iti 
		JOIN segments ON segments.id = iti 
		GROUP BY compositions.id) -- establish a relation between the two table with the id number

	UPDATE compositions
	SET geom = a.geom
	FROM a
	WHERE a.id = compositions.id; -- create the geometry in function of the compositions id
	
END IF;
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER make_routes
AFTER UPDATE or INSERT or DELETE
ON segments
FOR EACH ROW
EXECUTE FUNCTION make_routes();