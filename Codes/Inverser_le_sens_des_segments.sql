/******** Reverse last segment WHERE last point of last segment intersect left segment ********/

WITH
	a AS (SELECT compositions.id AS compoid, segments.id AS segid, segments.geom
		FROM compositions join segments ON segments.id = compositions.segments[cardinality(segments)]
		WHERE cardinality(segments)>1),
	b AS (SELECT compositions.id AS compoid, segments.id AS segid, segments.geom
		FROM compositions join segments ON segments.id = compositions.segments[cardinality(segments)-1]
		WHERE cardinality(segments)>1),
	c AS (SELECT a.segid FROM a join b ON a.compoid = b.compoid
		WHERE st_intersects(st_endpoint(a.geom), b.geom))
	
UPDATE segments
SET geom = st_reverse(segments.geom)
FROM c 
WHERE segments.id = c.segid;

/******* Reverse segments WHERE first point of left segment intersect right segment ************/

WITH 
	a AS (SELECT compositions.id, ordinality AS num, segid, segments.geom
		FROM compositions, UNNEST(segments) WITH ordinality AS segid 
		JOIN segments ON segments.id = segid 
		GROUP BY segid, compositions.id, num, segments.geom),
	b AS (SELECT a.segid
		FROM a join a b ON a.id = b.id AND a.num+1 = b.num
		WHERE st_intersects(st_startpoint(a.geom), b.geom)
		GROUP BY a.segid)
	
UPDATE segments
SET geom = st_reverse(segments.geom)
FROM b
WHERE segments.id = b.segid;
