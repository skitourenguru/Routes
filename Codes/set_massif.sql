/* Il faut avoir dans la BD la couche districts de Météo France.*/

WITH 
	district as(
	SELECT geometry 
	FROM districts 
	WHERE id = 6)

/* id correspond au numéro du district météo france :
1 : Chablais, 2 : Aravis, 3: Mont-Blanc, 4 : Bauges, 5: Beaufortain, 6: Tarentaise,
7: Chartreuse, 8: Belledonne, 9: Maurienne, 10: Vanoise, 11 : Haut-Maurienne, 
12 : Grandes Rousse, 13 : Cerces, 14: Vercors, 15 : Oisans, 16 : Écrins-Est,
17 : Queyras, 18 : Dévoluy, 19 : Écrins-Sud, 20 : Embrunais, 21 : Ubaye, 22 */

UPDATE compositions
SET massif = 'Tarentaise'
	FROM district 
	WHERE St_Contains(district.geometry, compositions.geom) AND massif IS NULL