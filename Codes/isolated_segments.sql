-- segments isolés, i.e. n'étant pas dans la table compositions

select segments.* from segments where segments.id not in (select unnest(segments) from compositions) and segments.importance = 0
