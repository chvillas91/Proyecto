""" 
Imagina que esta API es una biblioteca de peliculas:
La funcion load_movies() es como una biblioteca que carga el catalogo de libros (peliculas) cuando se abre la biblioteca.
La funcion get_movies() muestra todo el catalogo cuando alguien lo pide.
La funcion get_movie(id) es como si alguien preguntara por un libro especifico es decir, por un coidgo de identificacion.
La funcion chatbot (query) es un asistente que busca peliculas segun palabras clave y sinonimo.
La funcion get_movies_by_category(category) ayuda a encontrar peliculas segun su genero (accion, comedia, etc...)
"""

# Importamos las herramientas necesarias para continuar nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API, HTTPException nos ayuda a manejar errores  # noqa: F401
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse nos ayuda a manejar respuestas HTML, JSONResponse nos ayuda a manejar respuestas en formato JSON
import pandas as pd # pandas nos ayuda a manejar datos en tablas como si fuera un Excel
import nltk # nltk es una libreria para procesar texto y analizar palabras
from nltk.tokenize import word_tokenize # word_tokenize nos ayuda a tokenizar texto, es decir, a convertirlo en palabras
from nltk.corpus import wordnet # wordnet es una libreria para analizar sinonimos

# indicamos la ruta donde nltk buscara los datos descargados en nuestro computador
nltk.data.path.append(r'C:\Users\Christian Villa S\AppData\Roaming\nltk_data')

# Descarga las herramientas necesarias de NLTK para el analisis de palabras
nltk.download('punkt_tab')
nltk.download('punkt') # Paquete para dividir frases en palabras
nltk.download('wordnet') # Paquete para encontrar sinonimos en palabras 

# Función para cargar las peliculas desde un archivo csv.
def load_movies():
    # Leemos el archivo que contiene información de peliculas y seleccionamos la columnas mas importantes
    # df = pd.read_csv("Dataset/netflix_titles.cvs")[['show_id','type','title','director','cast','country','date_added','release_year','rating','duration','listed_in','description']]
    df = pd.read_csv("./Dataset/netflix_titles.csv")[['show_id','title','release_year','listed_in','rating','description']]
    
    # Renombramos las columnas para que sean mas felices de entender    
    df.columns = ['Id','Title','Year','Category','Rating','Overview']
    
    # Llenamos los espacios vacios con texto vacio y convertimos los datos en una lista de diccionario
    return df.fillna('').to_dict(orient='records')

# Cargamos las peliculas al inicar la API para no leer el archivo cada vez que alguien pregunte por ellas 
movies_list = load_movies()

# Fucnion para encontrar sinonimos de una palabra
def get_synonyms(word):
    # Usamos wordnet para encontrar distintas palabras q significan lo mismo
    return{lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Creamos la aplicacion FastAPI, que sera el mator de nuestra API
# Esta inicializa la API con una version
app = FastAPI(title="Mi Aplicacion de peliculsa", version="1.0.0")

# Ruta de inicio: Cuando alguien entra a la API si espesificar nada, vera un mensaje de bienvenida.
@app.get('/', tags=['Home'])
def home():
    # cuando entramos en el navegador a http://127.0.0.1:8000 veremos un mensaje de bienvenida 
    return HTMLResponse('<h1>Bienvenido a la API de Peliculas</h1>')
       
# Obtenemos la lista de peliculas
# Creamos una ruta para obtener todas las peliculas
# Ruta para optener todas las peliculas
@app.get('/movies', tags=['Movies'])
def get_movies():
    # Si hay peliculas, las enviamos , si no mostramos error 
    return movies_list or HTMLResponse(status_code=500, detail="No hay datos de peliculas disponibles")

# ruta para obtener una película específica por su ID
@app.get('/movies/{Id}', tags=['Movies'])
def get_movie(id: str):
     # buscamos en la lista de películas la que tenga el mismo ID
     return next((m for m in movies_list if m ['Id'] == id), {"detalle": "película no encontrada"})
 
 # Ruta del chatbot que responde con peliculas segun palabras claves de la categoria
@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la consulta en palabras clave, para entender mejor la intension del usuario
    query_words = word_tokenize(query.lower())
    # buscamos sinonomos delas palabras claves para ampliar la busqueda 
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)
    
    # Filtramos la lista de peliculas buscando coinsidencias en la categoria
    results = [m for m in movies_list if any (s in m ['Category'].lower() for s in synonyms)]
    
    # si encontramos las peliculas, enviamos la lista de peliculas; sino, mostramos un mensaje de que no se encontraron considencias
    return JSONResponse (content={
        "respuesta": "aqui tienes algunas peliculas relacionadas." if results else "No encontre peliculas en esa categoria.",
        "peliculas": results
    })
    
# Ruta para buscar películas por categoría específica
@app.get ('/movies/by_category/', tags=['Movies'])
def get_movies_by_category(category: str):
    #filtramos la lista de películas buscando coincidencias en la categoría ingresada
    return [m for m in movies_list if category.lower() in m['Category'].lower()]
