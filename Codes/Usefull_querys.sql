***********************************************************************************************************
************************************ Usefull querys *******************************************************
***********************************************************************************************************

	
-- Add a segment at the begining of an array

UPDATE compositions
SET segments = array_prepend(1981, segments)
WHERE 1980 = ANY(segments)

	/* In this example, segment 1981 is add at all routes where segment 989 is present */ 

*********************************************************************************************************
	
-- Insert a segment in the middle of an array 				

UPDATE compositions
SET segments = segments[:array_position(segments, 3267)]  -- id at the left of the new segment.
	||3269||                                          -- id of the new segment.
	segments[array_position(segments, 3267)+1:]       -- id at the left of the new segment.
WHERE 3279 = ANY(segments)   				  -- id at the right of the new segment. 

	/*In this example, segment 3269 is insert between segment 3267 and 3279 */

*********************************************************************************************************
	
-- Add a segment at the end of the array

UPDATE compositions
SET segments = array_append(segments, 3400)
WHERE 972 = ANY(segments)
	
	/* In this example, segment 3400 is add at all routes where segment 972 is present */ 
	
*********************************************************************************************************

-- Supprimer un segment 

UPDATE compositions
SET segments = array_remove(segments, 3269)
WHERE 3265 = ANY(segments)

/* In this example, segment 3269 is delete
in all routes where segment 3265 is present */

*********************************************************************************************************
*************************** Change data type of segments column *****************************************
*********************************************************************************************************
	
-- Text to Array

ALTER TABLE compositions
	ALTER segments TYPE INTEGER[] USING string_to_array(segments, ',')::int[];

-- Array to Text

ALTER TABLE compositions
    ALTER segments TYPE TEXT USING array_to_string(segments, ',');
