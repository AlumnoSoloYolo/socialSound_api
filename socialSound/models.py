from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from datetime import timedelta



class UsuarioManager(BaseUserManager):
   def create_user(self, nombre_usuario, email, password=None, **extra_fields):
       if not email:
           raise ValueError('Email es requerido')
       email = self.normalize_email(email)
       user = self.model(nombre_usuario=nombre_usuario, email=email, **extra_fields)
       user.set_password(password)
       user.save()
       return user

   def create_superuser(self, nombre_usuario, email, password=None, **extra_fields):
       extra_fields.setdefault('is_staff', True)
       extra_fields.setdefault('is_superuser', True)
       return self.create_user(nombre_usuario, email, password, **extra_fields)
   

class Usuario(AbstractBaseUser, PermissionsMixin):
    
    CLIENTE = 1
    MODERADOR = 2
    ROLES = (
        (CLIENTE, 'cliente'),
        (MODERADOR, 'moderador'),
    )
    nombre_usuario = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    ciudad = models.CharField(max_length=150, blank=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil/', default='fotos_perfil/default_profile.png', blank=True)
    fecha_nac = models.DateField(null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    rol = models.PositiveIntegerField(choices=ROLES, default=CLIENTE)

    objects = UsuarioManager()

    USERNAME_FIELD = 'nombre_usuario'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
            return self.nombre_usuario

    # Métodos para gestionar seguidores
    def seguir(self, otro_usuario):
            # Permite que este usuario siga a otro usuario
            if otro_usuario != self:  # No se puede seguir a uno mismo
                Seguidores.objects.get_or_create(seguidor=self, seguido=otro_usuario)

    def dejar_de_seguir(self, otro_usuario):
            # Permite que este usuario deje de seguir a otro usuario
            Seguidores.objects.filter(seguidor=self, seguido=otro_usuario).delete()

    def obtener_seguidores(self):
            # Devuelve una lista de usuarios que siguen a este usuario
            return Usuario.objects.filter(seguidores__seguido=self)  # Cambiado a 'seguido=self'

    def obtener_seguidos(self):
            # Devuelve una lista de usuarios a los que este usuario sigue
            return Usuario.objects.filter(siguiendo__seguidor=self)
        

class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, related_name="cliente", on_delete=models.CASCADE)
    genero_favorito = models.CharField(max_length=100, blank=True, null=True)
    artista_favorito = models.CharField(max_length=100, blank=True, null=True)
    acepta_terminos = models.BooleanField(default=False)

class Moderador(models.Model):
    usuario = models.OneToOneField(Usuario, related_name="moderador", on_delete=models.CASCADE)
    experiencia_moderacion = models.PositiveIntegerField(default=0)
    area_especialidad = models.CharField(max_length=100, blank=True, null=True)  # Añadido null=True
    codigo_moderador = models.CharField(max_length=10, unique=True, blank=True, null=True)  # Añadido null=True
    


class Seguidores(models.Model):
    seguidor = models.ForeignKey(Usuario, related_name="seguidores", on_delete=models.CASCADE)
    seguido = models.ForeignKey(Usuario, related_name="siguiendo", on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('seguidor', 'seguido')  # Evita duplicados

    def __str__(self):
        return f'{self.seguidor.nombre_usuario} sigue a {self.seguido.nombre_usuario}'


# Modelo Album
class Album(models.Model):
    titulo = models.CharField(max_length=200)
    artista = models.CharField(max_length=200)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="albumes")
    fecha_subida = models.DateField(default=timezone.now)
    portada = models.ImageField(upload_to='album_portadas/', blank=True)
    descripcion = models.TextField(blank=True)
    reposts = models.ManyToManyField(Usuario, related_name='reposts_albumes', blank=True)

    def __str__(self):
        return self.titulo


# Modelo Detalle del Álbum (OneToOne)
class DetalleAlbum(models.Model):
    album = models.OneToOneField(Album, on_delete=models.CASCADE, related_name='detalle_album')
    productor = models.CharField(max_length=200)
    estudio_grabacion = models.CharField(max_length=200, blank=True)
    numero_pistas = models.PositiveIntegerField()
    sello_discografico = models.CharField(max_length=100, blank=True)

    @property
    def numero_comentarios(self):
        return self.album.comentario_set.count()
    
    @property
    def numero_reposts(self):
        return self.album.reposts.count()

    def incrementar_reproducciones(self):
        self.reproducciones += 1
        self.save()


# Modelo de Estadísticas del Álbum (OneToOne)
class EstadisticasAlbum(models.Model):
    album = models.OneToOneField(Album, on_delete=models.CASCADE)
    reproducciones = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    comentarios = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Estadísticas del álbum {self.album.titulo}'


# Modelo de Canciones
class Cancion(models.Model):
    CATEGORIAS_CHOICES = [
        ('rock', 'Rock'),
        ('jazz', 'Jazz'),
        ('metal', 'Metal'),
        ('electronica', 'Electrónica'),
        ('pop', 'Pop'),
        ('hiphop', 'Hip-Hop'),
        ('reggae', 'Reggae'),
        ('blues', 'Blues'),
        ('classical', 'Clásica'),
        ('country', 'Country'),
        ('dance', 'Dance'),
        ('disco', 'Disco'),
        ('dubstep', 'Dubstep'),
        ('edm', 'EDM (Electronic Dance Music)'),
        ('funk', 'Funk'),
        ('gospel', 'Gospel'),
        ('grunge', 'Grunge'),
        ('hardrock', 'Hard Rock'),
        ('indie', 'Indie'),
        ('latin', 'Latina'),
        ('lofi', 'Lo-Fi'),
        ('opera', 'Ópera'),
        ('punk', 'Punk'),
        ('rnb', 'R&B (Rhythm and Blues)'),
        ('rap', 'Rap'),
        ('salsa', 'Salsa'),
        ('soul', 'Soul'),
        ('techno', 'Techno'),
        ('trance', 'Trance'),
        ('trap', 'Trap'),
        ('house', 'House'),
        ('ambient', 'Ambient'),
        ('acoustic', 'Acústica'),
        ('alternative', 'Alternativa'),
        ('chillout', 'Chillout'),
        ('drumandbass', 'Drum and Bass'),
        ('electro', 'Electro'),
        ('experimental', 'Experimental'),
        ('folk', 'Folk'),
        ('hardcore', 'Hardcore'),
        ('idm', 'IDM (Intelligent Dance Music)'),
        ('industrial', 'Industrial'),
        ('kpop', 'K-Pop'),
        ('metalcore', 'Metalcore'),
        ('newage', 'New Age'),
        ('noise', 'Noise'),
        ('progressiverock', 'Progressive Rock'),
        ('psytrance', 'Psytrance'),
        ('reggaeton', 'Reggaetón'),
        ('synthwave', 'Synthwave'),
        ('vaporwave', 'Vaporwave'),
        ('world', 'World Music'),
        ('ska', 'Ska'),
        ('tango', 'Tango'),
        ('grindcore', 'Grindcore'),
        ('postrock', 'Post-Rock'),
        ('drill', 'Drill'),
        ('shoegaze', 'Shoegaze'),
        ('glitch', 'Glitch'),
        ('breakbeat', 'Breakbeat'),
        ('emo', 'Emo'),
        ('christian', 'Cristiana'),
        ('jpop', 'J-Pop'),
        ('jrock', 'J-Rock'),
        ('futurebass', 'Future Bass'),
        ('progressivehouse', 'Progressive House'),
        ('moombahton', 'Moombahton'),
        ('dancehall', 'Dancehall'),
        ('dub', 'Dub'),
    ]
    etiqueta = models.CharField(max_length=50, choices=CATEGORIAS_CHOICES)
    titulo = models.CharField(max_length=200)
    artista = models.CharField(max_length=100)
    archivo_audio = models.FileField(upload_to='canciones/') #subir archivos .wav
    portada = models.ImageField(upload_to='cancion_portadas/', blank=True)
    fecha_subida = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='canciones', null=True, blank=True)
    likes = models.ManyToManyField(Usuario, through='Like', related_name='like_list', blank=True)
    reposts = models.ManyToManyField(Usuario, related_name='reposts_canciones', blank=True)

    def __str__(self):
        return self.titulo
    
    def obtener_duracion(self):
        try:
            if self.archivo_audio:
                audio = File(self.archivo_audio.path)
                if audio is not None:
                    duracion_segundos = float(audio.info.length)
                    return timedelta(seconds=int(duracion_segundos))
        except Exception as e:
            print(f"Error al obtener duración: {str(e)}")
        return timedelta()


# Modelo Detalle de Cancion (OneToOne)
class DetallesCancion(models.Model):
    cancion = models.OneToOneField(Cancion, on_delete=models.CASCADE, related_name='detalles')
    letra = models.TextField(blank=True)
    creditos = models.TextField(blank=True)
    duracion = models.DurationField(default=timedelta)
    idioma = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f'Detalles de {self.cancion.titulo}'
    
    @property
    def duracion_formateada(self):
        total_segundos = int(self.duracion.total_seconds())
        minutos = total_segundos // 60
        segundos = total_segundos % 60
        return f"{minutos:02d}:{segundos:02d}"


# Modelo de Playlist con relación ManyToMany a Cancion
class Playlist(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(max_length=255)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    canciones = models.ManyToManyField(Cancion, through='CancionPlaylist', related_name='cannciones')
    publica = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


# Tabla intermedia para Playlist y Cancion (ManyToMany con atributos extra)
class CancionPlaylist(models.Model):
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    orden = models.PositiveIntegerField(default=0)
    fecha_agregada = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('cancion', 'playlist')

    def __str__(self):
        return f'{self.cancion.titulo} en {self.playlist.nombre}'



# Modelo de Likes (ManyToMany con atributo extra de fecha)
class Like(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE)
    fecha_like = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('usuario', 'cancion')

    def __str__(self):
        return f'{self.usuario.nombre_usuario} le gustó {self.cancion.titulo}'


# Modelo de Comentarios
class Comentario(models.Model):
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(default=timezone.now)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.usuario.nombre_usuario} comentó en {self.album.titulo}'


# Modelo de Mensajes Privados
class MensajePrivado(models.Model):
    emisor = models.ForeignKey(Usuario, related_name='emisor', on_delete=models.CASCADE)
    receptor = models.ForeignKey(Usuario, related_name='receptor', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)

    def __str__(self):
        return f'Mensaje de {self.emisor.nombre_usuario} a {self.receptor.nombre_usuario}'


# Modelo de canciones guardadas (ManyToMany entre Usuario y Cancion)
class Guardado(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cancion = models.ForeignKey(Cancion, on_delete=models.CASCADE)
    fecha_guardado = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('usuario', 'cancion')

    def __str__(self):
        return f'{self.usuario.nombre_usuario} guardó {self.cancion.titulo}'
















































