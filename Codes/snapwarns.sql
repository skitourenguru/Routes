CREATE or REPLACE FUNCTION erreurs() RETURNS TRIGGER AS $$

BEGIN


DROP TABLE Erreurs;

CREATE TABLE Erreurs as 

/****************   Snap warn. Check if all the following segments are well snap *************************
*****************       and check if two followings segments are the same id      ************************/

WITH a AS (SELECT compositions.id as compoid, ordinality AS num, segid, st_collect(segments.geom) AS geom
		FROM compositions, UNNEST(segments) WITH ordinality AS segid 
		JOIN segments ON segments.id = segid 
		GROUP BY num, compoid, segid)

SELECT b.segid, null as num, b.geom 
FROM a join a b on a.compoid = b.compoid and a.num+1 = b.num
WHERE NOT st_intersects(a.geom, b.geom) or a.segid = b.segid
GROUP BY b.segid, b.geom

UNION 

/********************** Check if all the segments inside compositions exists ***************/

SELECT segid, ordinality AS num, geom
FROM compositions, unnest(segments) WITH ordinality AS segid
WHERE segid NOT IN (SELECT id FROM segments)

UNION 

/***************** Add random errors, just to keep the layer after Qgsi reload *************/

SELECT id , null as num, null as geom
FROM compositions
WHERE id = 530

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER erreurs_compo
AFTER UPDATE of segments
ON compositions
FOR EACH ROW
EXECUTE FUNCTION erreurs();

CREATE or REPLACE TRIGGER erreurs_snap
AFTER UPDATE 
ON segments
FOR EACH ROW
EXECUTE FUNCTION erreurs();
