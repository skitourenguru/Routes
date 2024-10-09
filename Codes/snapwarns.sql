/* You have to copy and paste this statement after you have click on execute sql inside Qgis */


/****************   Snap warn. Check if all the following segments are well snap *************************
*****************       and check if two followings segments have the same id      ************************/

WITH a AS (SELECT compositions.id as compoid, ordinality AS num, segid, st_collect(segments.geom) AS geom
		FROM compositions, UNNEST(segments) WITH ordinality AS segid
		JOIN segments ON segments.id = segid
		GROUP BY num, compoid, segid)

SELECT b.segid, null as num, b.geom
FROM a join a b on a.compoid = b.compoid and a.num+1 = b.num
WHERE st_distance(a.geom,b.geom) > 0.0000001 or a.segid = b.segid
GROUP BY b.segid, b.geom

UNION

/********************** Check if all the segments inside compositions exists ***************/

SELECT segid, ordinality AS num, geom
FROM compositions, unnest(segments) WITH ordinality AS segid
WHERE segid NOT IN (SELECT id FROM segments)

UNION

/***************** Add random errors, just to keep the layer after Qgis reload *************/

SELECT id , null as num, geom
FROM compositions
WHERE id = 530
