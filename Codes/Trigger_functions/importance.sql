CREATE or REPLACE FUNCTION importance() RETURNS TRIGGER AS $$
BEGIN

IF (TG_OP = 'UPDATE') Then

update segments
set importance = 0;

with
a as (select unnest(segments) as id, importance from compositions where importance = 0),  
b as (select unnest(segments) as id, importance from compositions where importance = 1),-- find the segments in compo where importance is 1
d as (select unnest(segments) as id, importance from compositions where importance = 2),
c as (select b.id, b.importance from b where b.id not in (select a.id from a) union
	  select d.id, d.importance from d where d.id not in (select a.id from a))-- find the segments in compo where importance is 1 but that are not use by other routes
update segments 
set importance = c.importance
from c
where c.id = segments.id;


END IF;
RETURN NEW;

END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER importance
AFTER UPDATE OF importance
ON compositions
FOR EACH ROW
EXECUTE FUNCTION importance();