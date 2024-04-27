CREATE or REPLACE FUNCTION split_and_merge() RETURNS TRIGGER AS $$
BEGIN

/*************************** Split segments *************************************/

IF EXISTS (SELECT id FROM public.segments GROUP BY id HAVING count(id)>1) THEN

    WITH 
        a AS (SELECT id FROM public.segments GROUP BY id HAVING count(id)>1),
        b as (SELECT compositions.id as compoid, ORDINALITY as num, segid, segments.geom
                FROM compositions, UNNEST(segments) WITH ordinality AS segid
                JOIN segments ON segments.id = segid),
        t as(SELECT c.segid, c.compoid                                      -- On cherche les segments inversés.
                FROM b JOIN b c on b.compoid = c.compoid and b.num+1 = c.num 
                JOIN a on c.segid = a.id
                WHERE st_intersects(st_endpoint(c.geom),(b.geom)))

    UPDATE public.compositions
    SET segments = segments[:array_position(segments,a.id)-1] -- Là où les segments sont inversés, on ajoute le nouveau segment à la gauche de l'ancien
                    ||(SELECT max(id)+1 FROM public.segments)::int|| 
                    segments[array_position(segments, a.id):]                
    FROM a, t
    WHERE a.id = ANY(segments) and  t.compoid = compositions.id;


    WITH 
        a AS (SELECT id FROM public.segments GROUP BY id HAVING count(id)>1),
        b as (SELECT compositions.id as compoid, ORDINALITY as num, segid, segments.geom
                FROM compositions, UNNEST(segments) WITH ordinality AS segid
                JOIN segments ON segments.id = segid),
        r as (SELECT c.segid, c.compoid, b.num as left, c.num as duplique, b.segid as leftid -- On cherche les segments dont le premiers points touche le dernier du segment précédant
                FROM b JOIN b c on b.compoid = c.compoid and b.num = c.num - 1
                JOIN a on c.segid = a.id
                WHERE st_intersects(st_startpoint(c.geom),(b.geom)))

    UPDATE public.compositions
    SET segments = segments[:array_position(segments,a.id)] -- Pour ces segments, on ajoute le nouveau segment à droite
                    ||(SELECT max(id)+1 FROM public.segments)::int|| 
                    segments[array_position(segments, a.id)+1:]               
    FROM a, r
    WHERE a.id = ANY(segments) and r.compoid = compositions.id;

    WITH 
        a AS (SELECT id FROM public.segments GROUP BY id HAVING count(id)>1),
        b as (SELECT compositions.id as compoid, ORDINALITY as num, segid, segments.geom
                FROM compositions, UNNEST(segments) WITH ordinality AS segid 
                JOIN segments ON segments.id = segid
                WHERE ordinality = 1)                       -- On cherche les premiers segments, où les segments faisant à eux seuls itinéraires
        
    UPDATE public.compositions
    SET segments = segments[:array_position(segments,a.id)] 
                    ||(SELECT max(id)+1 FROM public.segments)::int|| -- Dans ce cas, on ajoute le nouveau segment à droite de l'ancien
                    segments[array_position(segments, a.id)+1:]
                            
    FROM a, b
    WHERE b.segid = a.id and b.compoid = compositions.id;

    UPDATE public.segments
    SET  id  = (SELECT max(id)+1 FROM public.segments) -- On met à jour l'id du nouveau segment
    WHERE fid  = new.fid;

END iF;

/*************************** Merge segments *************************************/

IF (TG_OP = 'INSERT') THEN

	WITH
	a AS (SELECT seg, id FROM public.compositions, unnest(segments) AS seg 
	WHERE seg NOT IN (SELECT segments.id FROM public.segments)) -- On cherche les segments de compositions qui ne sont pas dans segments

	UPDATE public.compositions
	SET segments = array_remove(segments, a.seg) -- On les supprime.
	FROM a
	WHERE compositions.id = a.id;

END IF;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER split_and_merge
AFTER INSERT or DELETE
ON segments
FOR EACH ROW
EXECUTE FUNCTION split_and_merge();