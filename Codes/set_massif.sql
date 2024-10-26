WITH district AS (
    SELECT id, geometry 
    FROM districts
)
SELECT 
    CASE 
        WHEN district.id = 1 THEN 'Chablais'
        WHEN district.id = 2 THEN 'Aravis'
        WHEN district.id = 3 THEN 'Mont-Blanc'
        WHEN district.id = 4 THEN 'Bauges'
        WHEN district.id = 5 THEN 'Beaufortain'
        WHEN district.id = 6 THEN 'Tarentaise'
        WHEN district.id = 7 THEN 'Chartreuse'
        WHEN district.id = 8 THEN 'Belledonne'
        WHEN district.id = 9 THEN 'Maurienne'
        WHEN district.id = 10 THEN 'Vanoise'
        WHEN district.id = 11 THEN 'Haut-Maurienne'
        WHEN district.id = 12 THEN 'Grandes Rousses'
        WHEN district.id = 13 THEN 'Cerces'
        WHEN district.id = 14 THEN 'Vercors'
        WHEN district.id = 15 THEN 'Oisans'
        WHEN district.id = 16 THEN 'Écrins-Est'
        WHEN district.id = 17 THEN 'Queyras'
        WHEN district.id = 18 THEN 'Dévoluy'
        WHEN district.id = 19 THEN 'Écrins-Sud'
        WHEN district.id = 20 THEN 'Embrunais'
        WHEN district.id = 21 THEN 'Ubaye'
    END AS massif
FROM district
JOIN segments ON ST_Contains(district.geometry, segments.geom)
WHERE segments.id = (SELECT MAX(id) FROM segments);