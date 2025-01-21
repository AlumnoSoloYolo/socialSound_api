# redSocialMusica
        # Definir en qué consistirá mi página Web:

SocialSound es una aplicación basada en una red social para amantes de la música. La plataforma permite que los usuarios hacer login en su cuenta privada; puedan añadir su propia material; o descubrir y compartir distintos discos y canciones. Un usuario puede seguir a otros usuarios y ver las publicaciones de canciones y discos que sube o comparte en su feed. 

El usuario tiene un perfil personalizable que el resto de usuarios podrá ver.

Los usuarios pueden interactuar con otros usuarios por medio de likes, comentarios en publicaciones o mensajes directos. Además, los usuarios pueden guardar distintas canciones y añadirlas a playlists personalizadas.

        #  debe especificarse en que consiste cada modelo, cada atributo y cada parámetro usado. Y el esquema de modelo entidad-relación.


1. Modelo Usuario
Descripción: Representa a los usuarios de la plataforma.
Atributos:
nombre_usuario: CharField (máx. 100 caracteres) - Nombre único del usuario.
password: CharField (máx. 100 caracteres) - Contraseña del usuario (almacenada de forma encriptada).
bio: TextField (opcional) - Biografía del usuario.
ciudad: CharField (máx. 150 caracteres) - Ciudad del usuario.
foto_perfil: ImageField (opcional) - Imagen de perfil del usuario.
fecha_nac: DateField - Fecha de nacimiento del usuario.

2. Modelo Seguidores
Descripción: Representa la relación de seguimiento entre los usuarios.
Atributos:
seguidor: ForeignKey a Usuario - Usuario que sigue a otro.
seguido: ForeignKey a Usuario - Usuario que es seguido.
fecha_inicio: DateTimeField - Fecha en que se inició el seguimiento.

3. Modelo Album
Descripción: Representa un álbum musical.
Atributos:
titulo: CharField (máx. 200 caracteres) - Título del álbum.
artista: CharField (máx. 200 caracteres) - Artista del álbum.
usuario: ForeignKey a Usuario - Usuario que crea el álbum.
fecha_lanzamiento: DateField - Fecha de lanzamiento del álbum.
portada: ImageField (opcional) - Portada del álbum.
descripcion: TextField (opcional) - Descripción del álbum.
reposts: ManyToManyField a Usuario (opcional) - Usuarios que han compartido el álbum.

4. Modelo DetalleAlbum
Descripción: Contiene información adicional sobre un álbum.
Atributos:
album: OneToOneField a Album - Álbum asociado.
productor: CharField (máx. 200 caracteres) - Productor del álbum.
estudio_grabacion: CharField (máx. 200 caracteres, opcional) - Estudio donde se grabó el álbum.
numero_pistas: PositiveIntegerField - Número de pistas en el álbum.
sello_discografico: CharField (máx. 100 caracteres, opcional) - Sello discográfico del álbum.
5. Modelo EstadisticasAlbum

Descripción: Contiene estadísticas de un álbum.
Atributos:
album: OneToOneField a Album - Álbum asociado.
reproducciones: PositiveIntegerField (valor por defecto 0) - Número de reproducciones del álbum.
likes: PositiveIntegerField (valor por defecto 0) - Número de "me gusta" del álbum.
comentarios: PositiveIntegerField (valor por defecto 0) - Número de comentarios en el álbum.

6. Modelo Cancion
Descripción: Representa una canción musical.
Atributos:
etiqueta: CharField (máx. 50 caracteres) - Categoría de la canción (ej. rock, pop).
titulo: CharField (máx. 200 caracteres) - Título de la canción.
artista: CharField (máx. 100 caracteres) - Artista de la canción.
archivo_audio: FileField - Archivo de audio de la canción.
portada: ImageField (opcional) - Portada de la canción.
fecha_subida: DateTimeField (valor por defecto: hora actual) - Fecha en que se subió la canción.
usuario: ForeignKey a Usuario - Usuario que subió la canción.
album: ForeignKey a Album (opcional) - Álbum al que pertenece la canción.
likes: ManyToManyField a Usuario (opcional) - Usuarios que le han dado "me gusta" a la canción.
reposts: ManyToManyField a Usuario (opcional) - Usuarios que han compartido la canción.

7. Modelo DetalleCancion
Descripción: Contiene información adicional sobre una canción.
Atributos:
cancion: OneToOneField a Cancion - Canción asociada.
letra: TextField (opcional) - Letra de la canción.
creditos: TextField (opcional) - Créditos de la canción.
duracion: DurationField - Duración de la canción.
idioma: CharField (máx. 50 caracteres, opcional) - Idioma de la canción.

8. Modelo Playlist
Descripción: Representa una lista de reproducción de canciones.
Atributos:
nombre: CharField (máx. 100 caracteres) - Nombre de la lista de reproducción.
descripcion: TextField (máx. 255 caracteres) - Descripción de la lista de reproducción.
fecha_creacion: DateTimeField (valor por defecto: hora actual) - Fecha de creación de la lista de reproducción.
usuario: ForeignKey a Usuario - Usuario que creó la lista de reproducción.
canciones: ManyToManyField a Cancion (a través de CancionPlaylist) - Canciones en la lista de reproducción.
publica: BooleanField (valor por defecto: True) - Indica si la lista de reproducción es pública.

9. Modelo CancionPlaylist
Descripción: Tabla intermedia que relaciona Playlist y Cancion.
Atributos:
cancion: ForeignKey a Cancion - Canción en la lista de reproducción.
playlist: ForeignKey a Playlist - Lista de reproducción que contiene la canción.
orden: PositiveIntegerField (valor por defecto: 0) - Orden de la canción en la lista de reproducción.
fecha_agregada: DateTimeField (valor por defecto: hora actual) - Fecha en que se agregó la canción a la lista de reproducción.

10. Modelo Like
Descripción: Representa los "me gusta" dados a las canciones.
Atributos:
usuario: ForeignKey a Usuario - Usuario que dio "me gusta".
cancion: ForeignKey a Cancion - Canción a la que se le dio "me gusta".
fecha_like: DateTimeField (valor por defecto: hora actual) - Fecha en que se dio "me gusta".

Tipos de Atributos:
CharField: Se usa para cadenas cortas (nombres, títulos).
TextField: Se usa para cadenas más largas (biografías, letras).
DateField: Se usa para fechas.
DateTimeField: Se usa para fechas y horas.
PositiveIntegerField: Se usa para números enteros positivos (número de pistas, likes).
DurationField: Se usa para representar duraciones de tiempo.
ImageField: Se usa para cargar imágenes.
FileField: Se usa para cargar archivos (audio).
BooleanField: Se usa para valores verdadero/falso.
ManyToManyField: Se usa para relaciones de muchos a muchos.


        # Esquema de Modelo Entidad-Relación (ERD):


Relación Usuario

Relación 1 a N con Seguidores: Un usuario puede seguir a muchos otros usuarios (relación "seguidor").
Relación 1 a N con Album: Un usuario puede crear muchos álbumes.
Relación 1 a N con Cancion: Un usuario puede subir muchas canciones.
Relación N a N con Cancion a través de Like: Un usuario puede dar "me gusta" a muchas canciones, y una canción puede tener "me gusta" de muchos usuarios.
Relación N a N con Album a través de reposts: Un usuario puede repostear muchos álbumes, y un álbum puede ser reposted por muchos usuarios.
Relación N a N con Cancion a través de reposts: Un usuario puede repostear muchas canciones, y una canción puede ser reposted por muchos usuarios.
Relación 1 a N con Playlist: Un usuario puede crear muchas listas de reproducción.
Relación N a N con Cancion a través de Guardado: Un usuario puede guardar muchas canciones, y una canción puede ser guardada por muchos usuarios.


Relación Seguidores

Relación N a 1 con Usuario (seguidor): Cada relación de seguimiento tiene un usuario que es el "seguidor".
Relación N a 1 con Usuario (seguido): Cada relación de seguimiento tiene un usuario que es "seguido".
Relación única entre los usuarios: Un usuario no puede seguir al mismo usuario más de una vez (garantizado por unique_together).


Relación Album

Relación 1 a 1 con DetalleAlbum: Cada álbum tiene detalles específicos relacionados con él.
Relación 1 a 1 con EstadisticasAlbum: Cada álbum tiene estadísticas específicas relacionadas con él.
Relación 1 a N con Cancion: Un álbum puede contener muchas canciones.
Relación N a N con Usuario a través de reposts: Un álbum puede ser reposted por muchos usuarios, y un usuario puede repostear muchos álbumes.

Relación DetalleAlbum

Relación 1 a 1 con Album: Cada detalle del álbum está vinculado a un álbum específico.
Relación EstadisticasAlbum
Relación 1 a 1 con Album: Cada estadística del álbum está vinculada a un álbum específico.
Relación Cancion
Relación N a 1 con Album: Cada canción pertenece a un álbum específico (opcional, ya que puede ser nulo).
Relación 1 a N con DetalleCancion: Cada canción puede tener detalles específicos relacionados con ella.
Relación N a N con Usuario a través de Like: Una canción puede ser "gustada" por muchos usuarios y un usuario puede gustar muchas canciones.
Relación N a N con Usuario a través de reposts: Una canción puede ser reposted por muchos usuarios y un usuario puede repostear muchas canciones.
Relación 1 a N con Comentario: Una canción puede tener muchos comentarios.


Relación DetalleCancion

Relación 1 a 1 con Cancion: Cada detalle de la canción está vinculado a una canción específica.


Relación Playlist

Relación 1 a N con Usuario: Una lista de reproducción pertenece a un usuario específico.
Relación N a N con Cancion a través de CancionPlaylist: Una lista de reproducción puede contener muchas canciones, y una canción puede estar en muchas listas de reproducción.


Relación CancionPlaylist

Relación N a 1 con Cancion: Cada entrada de la tabla intermedia se refiere a una canción específica.
Relación N a 1 con Playlist: Cada entrada de la tabla intermedia se refiere a una lista de reproducción específica.
Relación única (cancion, playlist): Una canción no puede aparecer más de una vez en la misma lista de reproducción.


Relación Like

Relación N a 1 con Usuario: Cada "me gusta" está asociado a un usuario específico.
Relación N a 1 con Cancion: Cada "me gusta" está asociado a una canción específica.
Relación única (usuario, cancion): Un usuario no puede dar "me gusta" a la misma canción más de una vez.


Relación Comentario

Relación N a 1 con Cancion: Cada comentario está asociado a una canción específica.
Relación N a 1 con Usuario: Cada comentario está asociado a un usuario específico.


Relación MensajePrivado

Relación N a 1 con Usuario (emisor): Cada mensaje privado tiene un emisor que es un usuario específico.
Relación N a 1 con Usuario (receptor): Cada mensaje privado tiene un receptor que es un usuario específico.


Relación Guardado

Relación N a 1 con Usuario: Cada canción guardada está asociada a un usuario específico.
Relación N a 1 con Cancion: Cada canción guardada está asociada a una canción específica.
Relación única (usuario, cancion): Un usuario no puede guardar la misma canción más de una vez.


______________________________________________________________________________________________________________

PARTE 2: aclaraciones y especificaciones de URLs y Vistas

## ACLARACIONES ARCHIVOS MULTIMEDIA:

NO SE SIRVEN EN MODO PRODUCCIÓN. Si quieres verlo poner DEBUG = True


## Estructura de URLs

A continuación, se detallan las URLs disponibles en la aplicación, junto con las vistas correspondientes y sus funcionalidades.

### 1. Página de inicio

- URL: `/`
- Vista: `index`
- Descripción: Página principal con enlaces a todas las otras vistas de la aplicación.
- Requisito cumplido:
      -  index donde aaceder a todas las urls

### 2. Perfil del usuario

- URL: `/perfil_usuario/<nombre_usuario>/`
- Vista: `perfil_usuario`
- Descripción: Muestra el perfil del usuario especificado, incluyendo seguidos, seguidores y álbumes creados.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Relaciones ManyToMany (seguidores y seguidos).
  - Parámetros str
  - Uso de re_path en la url
  
### 3. Feed del usuario

- URL: `/usuario/<nombre_usuario>/feed/`
- Vista: `feed`
- Descripción: Muestra los álbumes subidos por los usuarios que el usuario especificado sigue.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Aggregates para calcular el total de likes en los álbumes.
  - Uso de limit
  - Parámetros str
  - Uso de order_by

### 4. Lista de álbumes

- URL: `/lista_albumes/<nombre_usuario>/`
- Vista: `lista_albumes`
- Descripción: Muestra una lista de todos los álbumes creados por el usuario especificado.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Relaciones OneToMany (álbumes del usuario).
  - Parámetros str
  - order_by

### 5. Detalles de un álbum

- URL: `/album/<int:album_id>/detalles_album/`
- Vista: `detalle_album`
- Descripción: Muestra los detalles de un álbum específico, incluyendo estadísticas.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Relaciones OneToOne (detalles y estadísticas del álbum).
  - Parámetros enteros

### 6. Listar canciones de un álbum

- URL: `/album/<int:album_id>/canciones/`
- Vista: `canciones_album`
- Descripción: Muestra todas las canciones que pertenecen a un álbum específico.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Parámetros enteros

### 7. Comentarios de un álbum

- URL: `/album/<int:album_id>/comentarios/`
- Vista: `comentarios_album`
- Descripción: Muestra todos los comentarios realizados en un álbum específico.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Relaciones OneToMany (comentarios del álbum).
  - Parámetros enteros
  - uso order_by

### 8. Detalles de una canción

- URL: `/cancion/<int:cancion_id>/detalles_cancion/`
- Vista: `detalle_cancion`
- Descripción: Muestra los detalles de una canción específica.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Parámetros enteros

### 9. Lista de playlists de un usuario

- URL: `/usuario/<nombre_usuario>/playlists/`
- Vista: `lista_playlist`
- Descripción: Muestra todas las playlists creadas por el usuario especificado.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Parámetros str

### 10. Contenido de una playlist

- URL: `/playlist/<int:playlist_id>/canciones/`
- Vista: `canciones_playlist`
- Descripción: Muestra todas las canciones que pertenecen a una playlist específica.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Parámetros enteros

### 11. Canciones guardadas por el usuario

- URL: `/canciones_guardadas/<nombre_usuario>/`
- Vista: `canciones_guardadas`
- Descripción: Muestra una lista de todas las canciones que el usuario ha guardado.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Parámetros str

### 12. Mensajes privados entre dos usuarios

- URL: `/mensajes_privados/<int:emisor_id>/<int:receptor_id>/`
- Vista: `mensajes_privados`
- Descripción: Muestra la interfaz de mensajes privados entre dos usuarios.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Parámetros enteros
  - filtros con OR y AND
  - Uso order_by


### 13. URL: Usuarios que un usuario específico no sigue
- Vista: `lista_no_sigue`
- Descripción: Muestra una lista de usuarios que el usuario actual no sigue.
- Requisitos cumplidos:
  - Uso de QuerySet, optimización y comentarios explicando funcionamiento de las vistas.
  - Parámetros str
  - Filtro con `None`: Se aplica un filtro que utiliza `None` en la tabla intermedia para determinar la relación de seguimiento.

## Requisitos cumplidos

1. 10 URLs con vistas correspondientes.
2. Uso de funciones vistas en clase y QuerySet para obtener datos entre tablas.
3. Comentarios en cada vista explicando su funcionalidad.
4. Manejo de relaciones ManyToMany, OneToOne y OneToMany.
5. Página de error personalizada para los cuatro tipos de errores.
6. Optimización de queries.
7. Uso de `re_path`, parámetros enteros y `str`.
8. Filtros con AND y OR, aggregate, relación reversa, `order_by`, limit y filtro con `None`.
9. Existencia de un índice desde donde se puede acceder a todas las URLs.



## Uso de templates tags (al menos 5)

 {% include 'header.html' %} en 'principal.html'
 {% block contenido %} {% endblock %} en 'principal.html'
 {% for %} {% endfor %} en 'album.html'
 {% empty %} en 'album.html'
 {% if %} {% else %} {% endif %} en 'album.html'

Son frecuentes en todo el proyecto, pero aquí especifico un ejemplo que muestra el uso de cada uno de ellos.


 ## Uso de al menos cinco operadores distintos
 {% if album.album.numero_pistas > 0 %} en 'album.html'
 {% if comentario.usuario.ciudad == None or comentario.usuario.ciudad != "" %} en 'comentario.html'
 {% if album.usuario and album.usuario.nombre_usuario %} en 'comentarios_album.html'
 {% if estadisticas_album.comentarios == 0 %} en 'detalle_album.html


 ## uso de distintos template filters
  <p>Estudio de Grabación: {{ album.album.estudio_grabacion|default:"Desconocido" }}</p> en 'album.html'
  <p>Ciudad: {{ comentario.usuario.ciudad|upper }}</p> en 'comentario.html'
  <p>Género: {{ album.descripcion|lower }}</p> en 'comentario.html'
  <p>{{ comentario.fecha_publicacion|date:"d/m/Y" }}</p> en 'comentario.html'
  <p>{{ comentario.contenido|linebreaks }}</p> en 'comentario.html'
  {% if comentarios|length > 0 %} en 'comentarios-album.html
  <p>Género: {{ album.descripcion|lower }}</p> en 'comentario.html'

Estoy especificando ejemplos de los distintos filtros que he utilizado, los cuales repito en el proyecto sumando más de 10. 
      
------------------------------------------------------------------------------------------------------------------------------

Lo primero que tienes que hacer para probar los CRUDS es logearte. Una vez logueado te redirijirá a la página principal donde
encontrarás distintas listas con todos los CRUDS.

LOG: NOMBRE_USUARIO=fran, PASSWORD='fran'

o haz tu propio registro

Validaciones del Sistema
Índice

CRUD Usuario
CRUD Álbum
CRUD Canción
CRUD Comentario
CRUD Playlist
Mensajes Privados

CRUD Usuario
CREATE - UsuarioModelForm
Email

Reglas:

Campo obligatorio
Patrón: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
Máximo 100 caracteres


Errores:

"Este campo es requerido"
"Introduce un correo electrónico válido"



Nombre Usuario

Reglas:

Campo obligatorio
Solo letras, números y guiones bajos: ^[a-zA-Z0-9_]+$
Debe ser único
Máximo 100 caracteres


Errores:

"Este campo es requerido"
"El nombre de usuario solo puede contener letras, números y guiones bajos"
"Nombre de usuario en uso"



Contraseña

Reglas:

Campo obligatorio
Mínimo 8 caracteres
Al menos una mayúscula, minúscula, número y carácter especial
Patrón: ^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$


Errores:

"Este campo es requerido"
"La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial (@$!%*?&)"



UPDATE - UsuarioUpdateForm

Mantiene las validaciones de email y nombre de usuario
Contraseña opcional

SEARCH - BusquedaAvanzadaUsuarioForm
Campos de Edad

Reglas:

Rango: 1-120 años
Validación cruzada de edad_min y edad_max


Errores:

"La edad mínima no puede ser mayor que la edad máxima"



CRUD Album
CREATE - AlbumModelForm
Título

Reglas:

Campo obligatorio
Máximo 200 caracteres
Único en combinación con artista


Errores:

"El título es obligatorio"
"El título no puede exceder los 200 caracteres"
"Ya existe un álbum con este título y artista"



Artista

Reglas:

Campo obligatorio
Máximo 200 caracteres


Errores:

"El artista es obligatorio"
"El nombre del artista no puede exceder los 200 caracteres"



SEARCH - BusquedaAvanzadaAlbumForm

Reglas:

Mínimo 3 caracteres para búsquedas por texto
Fechas coherentes


Errores:

"Debes especificar al menos un criterio de búsqueda"
"La fecha inicial no puede ser posterior a la fecha final"



CRUD Canción
CREATE - CancionForm
Título

Reglas:

Campo obligatorio
Entre 3 y 200 caracteres


Errores:

"El título es obligatorio"
"El título debe tener al menos 3 caracteres"
"El título no puede exceder los 200 caracteres"



Archivo Audio

Reglas:

Formatos: .wav, .mp3
Máximo 70MB


Errores:

"Solo se permiten archivos .wav o .mp3"
"El archivo no puede ser mayor a 70MB"



DetallesCancionForm

Créditos: Máximo 1000 caracteres

CRUD Comentario
CREATE - ComentarioModelForm

Reglas:

No vacío
No solo espacios
Máximo 1000 caracteres


Errores:

"El contenido es obligatorio"
"El comentario no puede estar vacío"
"El comentario no puede tener más de 1000 caracteres"



CRUD Playlist
CREATE - PlaylistForm

Nombre:

Mínimo 3 caracteres


Descripción:

Máximo 500 caracteres


Errores:

"El nombre de la playlist debe tener al menos 3 caracteres"
"La descripción no puede tener más de 500 caracteres"



Mensajes Privados
CREATE - MensajePrivadoForm

Reglas:

No vacío
No solo espacios
Entre 1 y 1000 caracteres


Errores:

"El mensaje no puede estar vacío o contener solo espacios"
"El mensaje debe contener al menos 1 carácter"
"El mensaje no puede exceder los 1000 caracteres"



# Widgets Utilizados en el Sistema
Input Básicos

TextInput:

Clase: 'form-control'
Usado en: nombres, títulos, artistas


EmailInput:

Clase: 'form-control'
Usado en: campos de email


PasswordInput:

Clase: 'form-control'
Usado en: contraseñas



Áreas de Texto

Textarea:

Clase: 'form-control'
Atributos comunes:

rows: 3-4
cols: 50


Usado en: biografías, descripciones, mensajes



Campos de Fecha

DateInput:

Clase: 'form-control'
type: 'date'
Usado en: fechas de nacimiento, búsquedas por fecha



Campos de Archivo

FileInput:

Clase: 'form-control'
Usado en: fotos de perfil, portadas, archivos de audio



Campos de Selección

Select:

Clase: 'form-control'
Usado en: etiquetas, categorías



Campos de Múltiple Selección

CheckboxSelectMultiple:

Clase: 'form-check-input me-1'
Usado en: selección de canciones en playlist



Checkbox Individual

CheckboxInput:

Clase: 'form-check-input'
Usado en: opciones booleanas (ej: playlist pública)



Campos Numéricos

NumberInput:

Clase: 'form-control'
Usado en: campos de edad   



# subir archivos

Configura los ajustes de medios:

Añade MEDIA_URL y MEDIA_ROOT en settings.py
Esto define dónde se guardarán los archivos subidos


Crea el modelo:

Define un modelo que incluya FileField o ImageField
FileField es para cualquier tipo de archivo
ImageField es específico para imágenes


Crea el formulario:

Usa ModelForm para manejar la subida de archivos
Especifica los campos que quieres incluir


Configura la vista:

Crea una vista que maneje tanto GET como POST
Asegúrate de incluir request.FILES al procesar el formulario


Configura las URLs:

Añade la ruta para tu vista
Incluye la configuración static() para servir los archivos en desarrollo


Crea la plantilla HTML:

Usa enctype="multipart/form-data" en el formulario
Incluye {% csrf_token %} para seguridad


--------------------------------------------------------------------------------------------------------------------------------

# SESIONES Y PERMISOS

## Tipos de Usuario y sus Funcionalidades

### 1. Cliente (Usuario normal)
Gestión de Perfil:
  - Crear y editar su propio perfil
  - Ver perfiles de otros clientes (no puede ver perfiles de moderadores ni administradores)

Contenido Musical:
  - Crear, editar y eliminar sus propios álbumes
  - Subir, editar y eliminar sus propias canciones
  - Ver todos los álbumes y canciones de la plataforma

Playlists:
  - Crear playlists propias
  - Añadir cualquier canción a sus playlists
  - Editar y eliminar sus propias playlists

Interacción Social:
  - Seguir a otros clientes
  - Comentar en álbumes
  - Editar y eliminar sus propios comentarios
  - Enviar mensajes privados a otros usuarios
  - Editar y eliminar sus propios mensajes

### 2. Moderador
Gestión de Usuarios:
  - Ver perfiles de todos los usuarios (excepto administradores)
  - No puede crear nuevo contenido propio

Control de Contenido:
  - Editar o eliminar cualquier álbum
  - Editar o eliminar cualquier canción
  - Editar o eliminar cualquier playlist
  - Editar o eliminar cualquier comentario
  - Editar o eliminar cualquier mensaje

Visualización:
  - Acceso total para ver todo el contenido
  - Ver estadísticas y reportes
  - Ver logs de actividad

Restricciones:
  - No puede crear álbumes propios
  - No puede crear playlists propias
  - No puede subir canciones
  - No puede seguir a otros usuarios

### Características Comunes
Ambos tipos de usuario pueden:
  - Iniciar y cerrar sesión
  - Ver el contenido público
  - Ver sus datos de sesión (última conexión, total de seguidores, total de seguidos, total de álbumes)
  - Usar el sistema de búsqueda (con restricciones según su rol)



Consideraciones: 

     - El formulario de registro tiene campos exclusivos para cada tipo de usuario
     - Acceder al login:
            Usuario cliente: DavidBowie Pssword: DavidBowie@1
            Usuario Moderador: Moderador1 Pssword: Cambiada@1

     - Las variables de sesión aparecen en el menú desplegable de arriba a la derecha, al igual que el log out

     - Filtro de búsqueda según tipo de usuario:
            El usuario moderador puede ver e interactuar con otros moderadores y todos los usuarios cliente.
            El usuario cliente solo puede ver e interactuar con otros usuarios. A menos que un moderador escriba un mensaje privado

     - En la página de login aparece un link para recuperar la contraseña.
            Puedes probar con el correo moderador1@socialsound.com para que aparezcan las indicaciones por consola
     
     



