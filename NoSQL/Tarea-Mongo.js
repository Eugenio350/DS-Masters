// Cargar dataset
const contents = [
    {
        content: "C:\\Users\\eugen\\Downloads\\movies.json",
        collection: "movies",
        idPolicy: "overwrite_with_same_id", //overwrite_with_same_id|always_insert_with_new_id|insert_with_new_id_if_id_exists|skip_documents_with_existing_id|abort_if_id_already_exists|drop_collection_first|log_errors
        //   Use the transformer to customize the import result
        transformer: (doc) => { //async (doc)=>{
            doc["importDate"] = new Date();
            doc["oid"] = mb.convert({ input: doc["oid"], to: "objectId", onError: "remain_unchanged", onNull: null });  //to: double|string|objectId|bool|date|int|long|decimal
            return doc; //return null skips this doc
        }
    }
];

mb.importContent({
    connection: "localhost",
    database: "Clases",
    fromType: "file",
    batchSize: 2000,
    contents
})

// Cambiar de schema
use test

// 1 Analizar con find la coleccion
db.movies.find()

// 2 Contar cuantos documentos (peliculas) tiene cargado Se muestra  salida
db.movies.count() // 28795

// 3. Insertar una película.
db.movies.insert({ "title": "Alien", "year": "1995", "cast": [], "genres": [] })

// 4. Borrar la pelicula insertada en el punto anterior
db.movies.deleteOne({ "title": "Alien", "year": "1995" })

// 5. Contar cuantas peliculas tienen actores (cast) que se llaman "and"
db.movies.find({ cast: { $in: ["and"] } }).count()

// 6. Actualizar los documentos cuyo actor tenga por error el valor "and"
db.movies.update(
    { cast: "and" },
    { $pull: { cast: "and" } },
    { multi: true }
)

// 7. Contar cuantas peliculas tienen el array 'cast' vacio
db.movies.find({ cast: { $eq: [] } }).count()

// 8. Actualizar todos los documentos que tengan el array cast vacio, 
// añadiendo un nuevo elemento dentro del array con valor Undefined
db.movies.update(
    { cast: { $eq: [] } },
    { $set: { cast: ["Undefined"] } },
    { multi: true })

// 9. Contar cuantos documentos (peliculas tienen el array genres vacio.
db.movies.find({ genres: { $eq: [] } }).count()

// 10. Actualizar todos los coumentos que tengan el array genres vacio.
// El tipo de genres debe seguir siendo un array
db.movies.update(
    { genres: { $eq: [] } },
    { $set: { genres: ["Undefined"] } },
    { multi: true })

// 11. Mostrar el año más reciente / actual que tenemos sobre las peliculas.
db.movies.find({}, { year: 1, _id: 0 }).sort({ "year": -1 }).limit(1)

// 12. Contar cuantas peliculas han salido en los últimos 20 años. Debe hacerse
// hacerse desde el último año que se tienen registradas las peliculas

var query = db.movies.find({}, { year: 1, _id: 0 }).sort({ "year": -1 }).limit(1).toArray()[0].year
db.movies.count({ year: { $gte: query - 19 } })

// 13. Contar cúantas películas han salido en la década de los 60 
// del (60 al 69 incluidos). Se debe hacer con el Framework de agregación

db.movies.find({ year: { $in: [1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969] } })

db.movies.aggregate([{ $match: { year: { $gte: 1960, $lte: 1969 } } },
{ $count: "total" }])

// 14. Mostrar el año con más peliculas mostrando el número de películas de ese año
// Reivsar si varios años pueden compartir tener el mayor número de peliculas
db.movies.aggregate([{
    $group: {
        _id: "$year", // agrupa por year
        pelis: { $sum: 1 }
    }
}, // Cuenta las peliculas
]).sort({ "pelis": -1 }) // Ordena las pelicula

// 15. Mostrar el año u años con menos peliculas mostrando el número de películas de ese año
db.movies.aggregate([{
    $group: {
        _id: "$year", // agrupa por year 
        pelis: { $sum: 1 }
    }
}, // Cuenta las peliculas
]).sort({ "pelis": 1 }) // Ordena las peliculas


// 16. Guardar en una nueva colección llamada "actors" realizando la fase $unwind por actor.
// Después, contar cuantos documentos existen en la nueva colección
db.movies.aggregate([
    { $unwind: "$cast" },
    { $project: { _id: 0, title: 1, year: 1, cast: 1, genres: 1 } },
    { $out: "actors" }
]);

db.actors.count()

// 17. Sobre actos, mostrar la lista con los 5 actores que han participado en más peliculas
// mostrando el número de películas en las que se ha participado. Importante, se necesita 
// previamente filtrar para descartar aquellos actores llamados "Undefined". Aclarar 
// que no se eliminan de la colección, solo que filtramos para que no aparezcan.

db.actors.aggregate([
    {$match: {cast: { $ne: "Undefined"}}},
    { $group: {
        _id: "$cast",
        cuenta: {$sum: 1}
    }},
    {$sort: {cuenta : -1}}}]).limit(5)

// 18. Sobre actors, agrupar por pelicula y año mostrando las 5 en las que más
// actores hayan participado, mostrando el número total de actores
db.actors.aggregate([
    {$match: {cast: { $ne: "Undefined"}}},
    { $group: {
        _id:{title: "$title", year: "$year"},
        cuenta: {$sum: 1}
    }},
    {$sort: {cuenta : -1}}}]).limit(5)
    
// 19. Sobre actors, mostrar los 5 actores cuya carrera haya sido la más larga. 
// para ello, se debe mostrar cuándo comenzó su carrera, cuándo finalizó y 
// cuántos años ha trabajado. Se necesita previamente filtrar para descartar
// aquellos actores llamados "Undefined"

db.actors.aggregate([
    {$match: {cast: {$ne: "Undefined"}}},
    { $group: {
        _id:{cast: "$cast"},
        comienza: {$min: "$year"},
        termina: {$max: "$year"}}},
        { $project: {
            _id: 0,
            cast: "$_id",
            comienza: 1,
            termina: 1,
            anos: {$subtract: ["$termina", "$comienza"]}}},
        {$sort: {anos: -1}}]).limit(6)
        
// 20. Sobre actors, guardar en nueva colección llamada "genres" realizando
// la fase $unwind por genres. Después, contar cuanto documentos existen en la
// nueva colección

db.actors.aggregate([
    { $unwind: "$genres"},
    { $project: { _id: 0, title:1, year:1, cast:1, genres:1}},
    { $out: "genres"}])
db.genres.count();

// 21. Sobre genres, mostrar los 5 documentos agrupados por "Año y Género " que
// más número de películas diferentes tienen mostrando el número total de peliculas

db.genres.aggregate([
    { $group: {
        _id: {year: "$year", genre: "$genres"},
        uniqueTitles: {$addToSet: "$title" }}},
        { $project: {
            _id: 0,
            year: "$_id.year",
            genre: "$_id.genre",
            Numero_de_peliculas: {$size: "$uniqueTitles"}}},
        {$sort: {Numero_de_peliculas: -1}},
        {$limit: 5}]);
        
// 22. Sobre genres, mostrar los 5 actores y los género en lo s que han participado
// con más número de géneros diferentes, se debe mostrar el número de géneros diferentes
// que se ha interpretado. Se necesita previamente filtrar para descartar los actores
// llamados undefined
db.genres.aggregate([
    {$match: {cast: {$ne: "Undefined"}}},
    {$group : {
        _id: "$cast",
        generos: {$addToSet: "$genres"} } },
    {$project: {
        _id: 0,
        actor: "$_id",
        numgeneros: {$size: "$generos"},
        generos: 1}},
        {$sort: {numgeneros: -1} },
        {$limit: 5}])
        
// 23. Sobre genres, mostrar las 5 peliculas y su año correspondiente en los que más géneros
// diferentes han sido catalogados, mostrando esos géneros y el número de géneros que contiene.
db.genres.aggregate([
    {$group: {
        _id: {title: "$title", year: "$year"}, // agrupa por titulo
        generos:{$addToSet: "$genres"}}}, // agrega generos para obtener generos unicos 
    { $project: {
        _id: 0,
        title: "$_id.title",
        year: "$_id.year",
        numgeneros: {$size: "$generos"}, // Cuenta el numero de generos unicos
        generos: 1}}, // incluye el genero de la variable anterior
    {$sort: { numgeneros: -1} }, // Ordenar
    {$limit: 5}])
    
// 24. Contar el número total de películas por género 
db.genres.aggregate([
    {$group: {
        _id: "$genres",
        totalMovies: {$sum: 1}}}])


// 25. Encontrar el promedio de puntacion de películas por año
db.movies.aggregate([
    {$group: {
        _id: "$year",
        averageScore: {$avg: "$score"}}}])
        
db.movies.find()

// 26. Listar las películas y su cantidad de actores excluyendo aquellas con "Undefined"

db.movies.aggregate([
    { $match: { cast: { $ne: "Undefined" } } },
    { $unwind: "$cast" },
    { $group: {
        _id: "$title",
        actorCount: { $sum: 1 }
    }},
    { $sort: { actorCount: -1 } }
]);

// 26. Encontrar número de peliculas producidas desde 2018 hasta 2023

db.movies.aggregate([
    { $match: { year: { $gte: 2018 } } }, // Asume que el año actual es 2023
    { $group: {
        _id: null, // Agrupa todos los documentos coincidentes
        numberOfMovies: { $sum: 1 } // Cuenta las películas
    }},
    { $project: {
        _id: 0, // Excluye el campo _id en el resultado final
        numberOfMovies: 1 // Incluye el recuento de películas
    }}
]);

