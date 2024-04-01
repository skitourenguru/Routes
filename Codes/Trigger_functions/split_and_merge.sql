CREATE or REPLACE FUNCTION split_and_merge() RETURNS TRIGGER AS $$

BEGIN

/* This function will not find by itself the name of the tables. You must name them "compositions" and "segments" and name the 
segments id list "segments" in the compositions table. */

/*************************** Split segments *************************************/

IF EXISTS (SELECT id FROM public.segments GROUP BY id HAVING count(id)>1) THEN


    WITH 
    a AS (SELECT id FROM public.segments GROUP BY id HAVING count(id)>1) -- find duplicate id

    UPDATE public.compositions
    SET segments = segments[:array_position(segments,a.id)] -- find in which position it is
    ||(SELECT max(id)+1 FROM public.segments)::int|| -- insert the last disponible id at him right
    segments[array_position(segments, a.id)+1:]
    FROM a
    WHERE a.id = ANY(segments);

            
    UPDATE public.segments
    SET  id  = (SELECT max(id)+1 FROM public.segments) -- update the id number of the new segment.
    WHERE fid  = new.fid;

END if;

/*************************** Merge segments *************************************/

IF (TG_OP = 'INSERT') THEN

	WITH
	a AS (SELECT seg, id FROM public.compositions, unnest(segments) AS seg 
	WHERE seg NOT IN (SELECT segments.id FROM public.segments)) -- find which segment is not in segments table

	UPDATE public.compositions
	SET segments = array_remove(segments, a.seg) -- remove it
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
