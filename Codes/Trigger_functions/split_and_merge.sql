CREATE or REPLACE FUNCTION split_and_merge() RETURNS TRIGGER AS $$
BEGIN

/************************************************* Split segments **************************************************/

/* Lorsqu'un segment est coupé en deux, ceux-ci partage un même id. Nous savons donc quel segment a été coupé en cherchant le id dupliqués. */

IF EXISTS (SELECT id FROM segments GROUP BY id HAVING count(id)>1) THEN

    WITH
        doublons AS (
            SELECT 	id
            FROM 	segments
            GROUP BY id
            HAVING count(id)>1
        ),

/* Le nouveau segment créé lors de la scission est ajouté APRÈS l'ancien, i.e. dans l'ordre des points, par ex. le résultat de la scission du segment 12 de coordonnées (1,2,3,4,5)
coupé à (3) sera : segment 12 (1,2,3), segment 13 (4,5). Le nouveau segment est discriminable de l'ancien avec la fonction NEW de postgres. Mais un segment peut-être partagé par
des compositions n'allant pas dans la même direction, ou un segment peut-être à l'envers. Tout l'art est de savoir s'il faut l'insérer à la droite ou à la gauche de l'ancien.
Trois cas de figures s'offrent à nous :
- Le segment d'un itinéraire composé d'un seul segment est coupé. Le seul moyen de savoir de quel côté insérer le nouveau segment est ici l'altitude.
- Le dernier segment d'un itinéraire est coupé. Si le dernier point du dernier segment touche le segment précédant il faut insérer le nouveau segment à gauche de l'ancien.
- Dans les autres cas, si le premier point du segment coupé touche le segment précédant, on insère à gauche sinon à droite. */

    /****************************************************************************************************************
    ******************************************** Segments uniques inversés ******************************************
    *****************************************************************************************************************/

                startpoint AS (
                    SELECT segments.id AS id,
                           st_value(rast, st_startpoint(geom), true) AS altitude
                    FROM	segments
                    JOIN 	mnt ON st_startpoint(geom) && mnt.rast
                ),
                endpoint AS (
                    SELECT	segments.id AS id,
                           	st_value(rast, st_endpoint(geom), true) AS altitude
                    FROM 	segments
                    JOIN 	mnt ON st_endpoint(geom) && mnt.rast
                ),
                segments_uniques AS (
                    SELECT 	segid,
                           	id
                    FROM 	compositions,
                         	unnest(segments) AS segid
                    WHERE 	cardinality(segments) = 1
                ),
        segment_unique_inverse AS (
			SELECT 	segments_uniques.id AS compoid
			FROM 	startpoint
			JOIN 	endpoint ON startpoint.id = endpoint.id
			JOIN 	segments_uniques ON segments_uniques.segid = endpoint.id
			JOIN 	doublons on doublons.id = endpoint.id
			WHERE 	startpoint.altitude > endpoint.altitude
        ),

    /****************************************************************************************************************
    ****************************** Premiers segments et segments du milieu inversés *********************************
    *****************************************************************************************************************/

                b AS (
                    SELECT 	compositions.id AS compoid,
						   	ORDINALITY AS num,
						  	segid,
						  	segments.geom
                    FROM 	compositions,
                         	UNNEST(segments) WITH ordinality AS segid
                    JOIN 	segments ON segments.id = segid
                ),
        premier_milieu_inverse AS (
                SELECT 	b.compoid
                FROM 	b JOIN b c ON b.compoid = c.compoid AND b.num+1 = c.num
                JOIN 	doublons ON doublons.id = b.segid
                WHERE 	st_startpoint(b.geom) && (c.geom)
        ),


    /****************************************************************************************************************
    ***************************************** Derniers segments inversés ********************************************
    *****************************************************************************************************************/

                avant_dernier AS (
                    SELECT 	segments[array_length(segments, 1) -1] AS segid,
                           	compositions.id AS compoid,
                          	segments.geom
                    FROM 	compositions
                    JOIN 	segments ON segments.id = segments[array_length(segments, 1) - 1]
                ),

                dernier AS (
					SELECT 	segments[array_length(segments, 1)] AS segid,
							compositions.id AS compoid,
							segments.geom
					FROM 	compositions
					JOIN 	segments ON segments.id = segments[array_length(segments, 1)]
					JOIN 	doublons ON doublons.id = segments[array_length(segments, 1)]
                ),
        dernier_inverse AS (
            SELECT 	dernier.compoid
            FROM 	dernier
            JOIN 	avant_dernier ON avant_dernier.compoid = dernier.compoid
            WHERE 	st_endpoint(dernier.geom) && avant_dernier.geom
        )


    UPDATE 	compositions
    SET 	segments = CASE
    WHEN   	compositions.id IN (SELECT segment_unique_inverse.compoid FROM segment_unique_inverse)
        OR 	compositions.id IN (SELECT premier_milieu_inverse.compoid FROM premier_milieu_inverse)
        OR 	compositions.id IN (SELECT dernier_inverse.compoid FROM dernier_inverse)
    THEN
        	segments[:array_position(segments,doublons.id)-1]
        	||(SELECT max(id)+1 FROM segments)::int||
       	 	segments[array_position(segments, doublons.id):]
    ELSE
        	segments[:array_position(segments,doublons.id)]
        	||(SELECT max(id)+1 FROM segments)::int||
        	segments[array_position(segments, doublons.id)+1:]
    END
    FROM 	doublons
    WHERE 	doublons.id = ANY(segments);



    -- On met à jour l'id du nouveau segment
    UPDATE 	segments
    SET  	id  = (SELECT max(id)+1 FROM segments)
    WHERE	fid  = new.fid;



END iF;

/*************************** Merge segments *************************************/

IF (TG_OP = 'INSERT') THEN

	WITH
        -- On cherche les segments de compositions qui ne sont pas dans segments
	    segments_inexistants AS (
            SELECT 	segid,
                   	id
            FROM 	compositions,
                 	unnest(segments) AS segid
	        WHERE 	segid NOT IN (SELECT segments.id FROM segments)
        )

    -- On les supprime.
	UPDATE 	compositions
	SET 	segments = array_remove(segments, segments_inexistants.segid)
	FROM 	segments_inexistants
	WHERE 	compositions.id = segments_inexistants.id;

END IF;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE or REPLACE TRIGGER split_and_merge
AFTER INSERT
ON segments
FOR EACH ROW
EXECUTE FUNCTION split_and_merge();
