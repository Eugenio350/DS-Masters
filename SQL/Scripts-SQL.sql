USE human_study_onu;

SELECT *
FROM countries;

USE human_study_ddl;
SELECT Country_id, Gender, Year,`Human Development Index`
FROM human_development;

# Hastags para comentarios # cool
SELECT ALL Country_id # Selecciona todos los country_id
FROM human_development;


SELECT DISTINCT Country_id
FROM human_development; 

## ALIAS Y LIMIT
SELECT Country_id AS ID, Year as Año, Gender 'Genero', 'Life Expectancy at Birth' AS 'Esperanza de vida' 
FROM human_development
LIMIT 40;

# Operadores Matematicos
SELECT Country_id as ID, `Life Expectancy at Birth` AS 'Esperanza de vida', `Life Expectancy at Birth`*2 AS Esperanza_vida_doble
FROM human_development;

SELECT Country_id as ID, `Life Expectancy at Birth` AS 'Esperanza de vida', `Life Expectancy at Birth`+20 AS Esperanza_vida_mas_veinte
FROM human_development;

SELECT Country_id as ID, `Life Expectancy at Birth` AS 'Esperanza de vida', `Life Expectancy at Birth`/2 AS Esperanza_vida_mitad
FROM human_development;

USE human_study_onu;

SELECT `Paid Leave Days`, `Paid Public Holidays`, `Paid Leave Days` + `Paid Public Holidays` AS Vacaiones_Totales
FROM paid_days_off
LIMIT 10;

SELECT *
FROM country_population
WHERE Population > 800000000;


SELECT *
FROM country_population
WHERE Population > 800000000
AND Year = 2020;

SELECT *
FROM country_population
WHERE NOT "country ID"  = 'CHN'
AND Year = 2020;

SELECT *
FROM country_population
WHERE Population > 800000000
AND YEAR = 2020
AND NOT `country ID` = 'CHN';


# AND OR
SELECT *
FROM country_population
WHERE YEAR = 2010 AND Population > 800000000 ;

USE human_study_ddl;
SELECT *
FROM human_development
WHERE GENDER="Male" AND `Country_id`="CHN" ;


USE human_study_ddl;
SELECT *
FROM human_development
WHERE (GENDER="Female" AND `Country_id`="ITA") OR (`GENDER`="Male" AND `Country_id`="CHN");

SELECT *
FROM human_development
WHERE Country_id = "ITA" OR Country_id = "CHN" OR Country_id="MEX";

## TAMBIEN ES POSIBLE
SELECT *
FROM human_development
WHERE Country_id IN ("ITA", "CHN", "MEX");

SELECT *
FROM human_development
WHERE NOT Country_id IN ("ITA", "CHN", "MEX");

SELECT * 
FROM human_development
WHERE Year BETWEEN 2010 AND 2012;

SELECT *
FROM human_development
WHERE Country_id BETWEEN "A" AND "B"; # Solo incluye la A no la B

USE human_study_onu;
# OPERADOR LIKE
SELECT `Country ID` AS ID, `Population` AS Poblacion, `Year` AS AÑO
FROM country_population
WHERE `Country ID` LIKE "A%"; # Unicamente los que empiezan con una A

SELECT `Country ID` AS ID, `Population` AS Poblacion, `Year` AS AÑO
FROM country_population
WHERE `Country ID` LIKE "%X%"; # CUALQUIER POSICION DE X 

# Funciones de agregacion
USE human_study_ddl;
SELECT COUNT(*) AS RECUENTO_FILAS,
		AVG(`Human Development Index`) AS Promedio_HDI,
        SUM(`Gross National Income Per Capita`) AS Suma_RPC,
        ROUND(MAX(`Life Expectancy at Birth`), 4)AS Maximo_vida,
        ROUND(MIN(`Mean Years of Schooling`), 2) AS Minimo_escuela
FROM human_development
GROUP BY `Country_id`, 2
HAVING Promedio_HDI>0.75;

SELECT DISTINCT `Country_id`, COUNT(*) AS RECUENTO_FILAS,
		ROUND(AVG(`Human Development Index`), 2) AS Promedio_HDI,
        SUM(`Gross National Income Per Capita`) AS Suma_RPC,
        ROUND(MAX(`Life Expectancy at Birth`), 4)AS Maximo_vida,
        ROUND(MIN(`Mean Years of Schooling`), 2) AS Minimo_escuela
FROM human_development
GROUP BY `Country_id`;

SELECT Country, Year, Gender,
avg(`Human Development Index`) AS Promedio_HDI
FROM  human_study_ddl.human_development
GROUP BY Country, Year, Gender
HAVING Promedio_HDI > 0.7;

SELECT Country, Year, Gender,
avg(`Human Development Index`) AS Promedio_HDI
FROM  human_study_ddl.human_development
GROUP BY Country, Year, Gender
HAVING Promedio_HDI > 0.7
ORDER BY Year DESC;

SELECT Country, Year, Gender,
avg(`Human Development Index`) AS Promedio_HDI
FROM  human_study_ddl.human_development
GROUP BY Country, Year, Gender
HAVING Promedio_HDI > 0.7
ORDER BY Year DESC, Country;

SELECT DISTINCT Year, `Country_id`, Gender,
COUNT(*) AS Recuento_Filas,
ROUND(AVG(`Human Development Index`), 2) AS Promedio_HDI,
ROUND(SUM(`Gross National Income Per Capita`), 2) AS Suma_RPC,
Round(MAX(`Life Expectancy at Birth`), 2) AS Edad_de_muerte_esperada,
ROUND(MIN(`Mean Years of Schooling`), 2) AS Minimo_escuela
FROM human_development
WHERE Year BETWEEN 2000 AND 2021
GROUP BY 1,2,3 # Se agrupa por Year, Country_id y Gender
HAVING Promedio_HDI>=0.75
ORDER BY Year ASC, Country_id Desc;

SELECT *
FROM human_study_ddl.human_development;

SELECT *
FROM human_study_on.countries;

## JOIN NATURAL
SELECT * FROM human_study_ddl.human_development
NATURAL JOIN human_study_onu.countries;

## INNER JOIN
SELECT * FROM human_study_ddl.human_development as E
INNER JOIN human_study_ddl.human_development ON human_study_onu.countries.`Country_id`;

SELECT *
FROM human_study_onu.countries;

USE human_study_onu;

SELECT h.country_id AS ID, c.Country AS País, `Human Development Index` AS HDI, Year
FROM `human_development` AS h INNER JOIN countries as c
ON h.`Country_id`=c.`Country_id`;

SELECT Country_id, `Human Development Index` AS HDI, Year, `Paid Leave Days`, `Paid Public Holidays`
FROM `human_development` AS h INNER JOIN `paid_days_off` as p
ON h.`Country_id`=p.`country ID`;

SELECT Country_id, h.Year, `Human Development Index`, `Population`
FROM `human_development` AS h INNER JOIN `country_population` AS cp
ON h.`Country_id` = cp.`country ID` AND h.Year=cp.Year;  # Inner Join Compuesto

SELECT Country_id, h.Year, `Human Development Index`, `Population`
FROM `human_development` AS h LEFT JOIN `country_population` AS cp # LEFT JOIN
ON h.`Country_id` = cp.`country ID` AND h.Year=cp.Year;


SELECT Country_id, h.Year, `Human Development Index`, `Population`
FROM `human_development` AS h RIGHT JOIN `country_population` AS cp # RIGHT JOIN
ON h.`Country_id` = cp.`country ID` AND h.Year=cp.Year;

# MULTIPLES JOIN

SELECT h.Country_id, h.Year, `Human Development Index`, `Population`, c.Country
FROM `human_development` AS h INNER JOIN `country_population` AS po # RIGHT JOIN
ON h.`Country_id` = po.`country ID` AND h.Year=po.Year
INNER JOIN countries as c
ON h.`Country_id`=c.`Country_ID`;


SELECT *
FROM `human_development` AS h JOIN `country_population` AS cp # RIGHT JOIN
ON h.`Country_id` = cp.`country ID` AND h.Year=cp.Year;

SELECT * FROM `human_development` LIMIT 10;
SELECT * FROM `countries` LIMIT 10;

SELECT Year, h.Country, h.`Life Expectancy at Birth`
FROM `human_development` as h INNER JOIN `countries` as c
ON h.Country_id =  c.Country_id;

# UNION
SELECT `country ID` as ID, Population as Poblacion, Year as ano
FROM `country_population`; # una tabla

SELECT `country ID` as ID, Population as Poblacion, Year as ano
FROM `country_population_2021`; # otra tabla
#nueva union 

SELECT `country ID` as ID, Population as Poblacion, Year as ano
FROM `country_population`
UNION
SELECT `country ID` as ID, Population as Poblacion, Year as ano
FROM `country_population_2021`; # UNION DE TABLAS COMPATIBLES

# CASE WHEN
SELECT `Country_id`, ROUND(AVG(`Human Development Index`), 2) AS HDI,
CASE 
	WHEN  ROUND(AVG(`Human Development Index`), 2) < 0.25 THEN "Bajo"
	WHEN  ROUND(AVG(`Human Development Index`), 2) >= 0.25 AND ROUND(AVG(`Human Development Index`),2) < 0.75 THEN "Medio"
	WHEN  ROUND(AVG(`Human Development Index`), 2) >= 0.75 THEN "Alto"
	ELSE "No hay medida"
END AS Categorias_hdi
FROM human_development
GROUP BY `Country_id`
ORDER BY 2, 1;

#SUBCONSULTAS
# Primera Consulta
SELECT Country, Gender, `Human Development Index`
FROM `human_development` 
WHERE YEAR=2020;

# Segunda Consulta
SELECT DISTINCT(`country ID`)
FROM country_population
WHERE Population > 8000000;

SELECT Country, Gender, `Human Development Index`
FROM `human_development` 
WHERE YEAR=2020
AND `Country_id` IN (SELECT DISTINCT(`country ID`)
FROM country_population
WHERE Population > 80000000);# para habitantes que tengan mas de 80millones

SELECT `Country_id`, Country, Gender, `Human Development Index`
FROM `human_development`
WHERE YEAR = 2020 AND `Country_id` IN(
SELECT `country ID`
FROM paid_days_off
WHERE `Paid Leave Days` + `Paid Public Holidays` > 43); 

# SUBCONSULTAS RELACIONADAS
SELECT `Country_id`, Promedio_Pais
FROM(SELECT `Country_id`, ROUND(AVG(`Human Development Index`), 2) AS Promedio_Pais
FROM `human_development` 
WHERE Year = 2020
GROUP BY `Country_id`) AS SUBCONSULTA;

SELECT `Country_id`, ROUND(AVG(`Human Development Index`), 2) AS Promedio_Pais
FROM `human_development` 
WHERE Year = 2020
GROUP BY `Country_id`;

# CREAR VISTA
CREATE VIEW SUBCONSULTA_VISTA AS
SELECT `Country_id`, Promedio_Pais
FROM(SELECT `Country_id`, ROUND(AVG(`Human Development Index`), 2) AS Promedio_Pais
FROM `human_development` 
WHERE Year = 2020
GROUP BY `Country_id`) AS SUBCONSULTA;

# FUNCIONES DE VENTANA 
SELECT `Country_id`, Year, Gender, 
AVG(`Human Development Index`) OVER() AS Promedio_HDI # Funcion Ventana
FROM `human_development`;

SELECT `Country_id`, Year, Gender, 
AVG(`Human Development Index`) OVER(PARTITION BY `Country_id`) AS Promedio_HDI_por_pais # Funcion Ventana, agrupando el promedio por pais
FROM `human_development`;

SELECT `Country_id`, Year, Gender, 
AVG(`Human Development Index`) OVER(PARTITION BY `Country_id`, Year) AS Promedio_HDI_por_pais_y_year # Funcion Ventana, agrupando el promedio por pais
FROM `human_development`;

SELECT `Country_id`, Year, Gender, 
AVG(`Human Development Index`) OVER(PARTITION BY `Country_id`, Year, Gender) AS Promedio_HDI_por_pais_year_gender # Funcion Ventana, agrupando el promedio por pais
FROM `human_development`;