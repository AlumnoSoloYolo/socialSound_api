from rest_framework import serializers
from .models import *


class UsuarioBasicoSerializer(serializers.ModelSerializer):
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    date_joined = serializers.DateTimeField(format="%d-%m-%Y", read_only=True)
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_usuario', 'email', 'foto_perfil', 
            'ciudad', 'rol', 'rol_display', 'date_joined'
        ]

class SeguidoresSerializerMejorado(serializers.ModelSerializer):
    seguidor = UsuarioBasicoSerializer(read_only=True)
    seguido = UsuarioBasicoSerializer(read_only=True)
    fecha_inicio = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = Seguidores
        fields = ['id', 'seguidor', 'seguido', 'fecha_inicio']

class ClienteSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioBasicoSerializer(read_only=True)
    
    class Meta:
        model = Cliente
        fields = ['id', 'usuario', 'genero_favorito', 'artista_favorito', 
                 'acepta_terminos']

class ModeradorSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioBasicoSerializer(read_only=True)
    
    class Meta:
        model = Moderador
        fields = ['id', 'usuario', 'experiencia_moderacion', 'area_especialidad', 
                 'codigo_moderador']

class UsuarioSerializer(serializers.ModelSerializer):
    rol_display = serializers.CharField(source='get_rol_display', read_only=True)
    seguidores = SeguidoresSerializerMejorado(source='siguiendo', many=True, read_only=True)
    seguidos = SeguidoresSerializerMejorado(source='seguidores', many=True, read_only=True)
    cliente = ClienteSerializerMejorado(read_only=True)
    moderador = ModeradorSerializerMejorado(read_only=True)
    seguidores_count = serializers.IntegerField(read_only=True)
    seguidos_count = serializers.IntegerField(read_only=True)
    fecha_nac = serializers.DateField(format="%d-%m-%Y", read_only=True)
    # foto_perfil_url = serializers.SerializerMethodField()

    # def get_foto_perfil_url(self, obj):
    #     if obj.portada:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(obj.foto_perfil.url)
    #     return None

    class Meta:
        model = Usuario
        fields = [
            'id', 'nombre_usuario', 'email', 'foto_perfil', 
            'ciudad', 'rol', 'rol_display', 'fecha_nac',
            'seguidores', 'seguidos', 'seguidores_count', 
            'seguidos_count', 'cliente', 'moderador', 'bio'
        ]

class AlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['id', 'titulo']



class DetallesCancionSerializer(serializers.ModelSerializer):
    duracion_formateada = serializers.SerializerMethodField()
    
    class Meta:
        model = DetallesCancion
        fields = ['letra', 'creditos', 'duracion', 'idioma', 'duracion_formateada']
    
    def get_duracion_formateada(self, obj):
        return obj.duracion_formateada

class DetalleAlbumSerializer(serializers.ModelSerializer):
    numero_comentarios = serializers.SerializerMethodField()
 
    
    class Meta:
        model = DetalleAlbum
        fields = ['productor', 'estudio_grabacion', 'numero_pistas', 
                 'sello_discografico', 'numero_comentarios']
    
    def get_numero_comentarios(self, obj):
        return obj.numero_comentarios

   

class EstadisticasAlbumSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadisticasAlbum
        fields = ['reproducciones', 'likes', 'comentarios']

class CancionSerializerMejorado(serializers.ModelSerializer):
    detalles = DetallesCancionSerializer(read_only=True)
    etiqueta_display = serializers.CharField(source='get_etiqueta_display', read_only=True)
    fecha_subida = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    usuario = UsuarioSerializer(read_only=True)
    likes = serializers.PrimaryKeyRelatedField(source='like_set.all', many=True, read_only=True)
    album_titulo = serializers.SerializerMethodField()
    portada_url = serializers.SerializerMethodField()
    archivo_audio_url = serializers.SerializerMethodField()

    
    def get_album_titulo(self, obj):
        return obj.album.titulo if obj.album else None
    
    def get_portada_url(self, obj):
        if obj.portada:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.portada.url)
        return None
    
    def get_archivo_audio_url(self, obj):
        if obj.archivo_audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.archivo_audio.url)
        return None
    
    class Meta:
        model = Cancion
        fields = [
            'id', 'titulo', 'artista', 'archivo_audio', 'archivo_audio_url', 'portada', 'portada_url',
            'fecha_subida', 'etiqueta', 'etiqueta_display', 'detalles',
            'usuario', 'likes', 'album_titulo'
        ]

class AlbumSerializerMejorado(serializers.ModelSerializer):
    canciones = CancionSerializerMejorado(many=True, read_only=True)
    detalle_album = DetalleAlbumSerializer(read_only=True)
    estadisticasalbum = EstadisticasAlbumSerializer(read_only=True)
    fecha_subida = serializers.DateField(format="%d-%m-%Y", read_only=True)
    usuario = UsuarioSerializer(read_only=True)
    
    class Meta:
        model = Album
        fields = [
            'id', 'titulo', 'artista', 'usuario', 'fecha_subida', 
            'portada', 'descripcion', 'canciones', 'detalle_album', 
            'estadisticasalbum'
        ]

class ComentarioSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    fecha_publicacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = Comentario
        fields = ['id', 'contenido', 'fecha_publicacion', 'album', 'usuario']

class LikeSerializerMejorado(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    fecha_like = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'usuario', 'cancion', 'fecha_like']

class CancionPlaylistSerializerMejorado(serializers.ModelSerializer):
    cancion = CancionSerializerMejorado(read_only=True)
    fecha_agregada = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = CancionPlaylist
        fields = ['cancion', 'orden', 'fecha_agregada']

class PlaylistSerializerMejorado(serializers.ModelSerializer):
    canciones = CancionPlaylistSerializerMejorado(source='cancionplaylist_set', many=True, read_only=True)
    fecha_creacion = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    usuario = UsuarioSerializer(read_only=True)
    total_canciones = serializers.SerializerMethodField()
    
    class Meta:
        model = Playlist
        fields = ['id', 'nombre', 'descripcion', 'fecha_creacion', 
                 'usuario', 'canciones', 'publica', 'total_canciones']
    
    def get_total_canciones(self, obj):
        return obj.canciones.count()

class MensajePrivadoSerializerMejorado(serializers.ModelSerializer):
    emisor = UsuarioSerializer(read_only=True)
    receptor = UsuarioSerializer(read_only=True)
    fecha_envio = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", read_only=True)
    
    class Meta:
        model = MensajePrivado
        fields = ['id', 'emisor', 'receptor', 'contenido', 'fecha_envio', 'leido']


import base64
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile

class UsuarioSerializerCreate(serializers.ModelSerializer):
    foto_perfil = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'email', 'password', 'bio', 'foto_perfil']
    
    def create(self, validated_data):
   
        foto_base64 = validated_data.pop('foto_perfil', '') or ''
        
       
        usuario = Usuario.objects.create_user(
            nombre_usuario=validated_data["nombre_usuario"],
            email=validated_data["email"],
            password=validated_data["password"],
            bio=validated_data.get("bio", "")
        )
        
    
        if foto_base64 and foto_base64.strip() and ';base64,' in foto_base64:
            try:
                formato, imgstr = foto_base64.split(';base64,')
                ext = formato.split('/')[-1]
                datos = ContentFile(base64.b64decode(imgstr))
                nombre_archivo = f"fotos_perfil/user_{usuario.id}.{ext}"
                
         
                import os
                directorio = os.path.join('media', 'fotos_perfil')
                if not os.path.exists(directorio):
                    os.makedirs(directorio)
                
                usuario.foto_perfil.save(nombre_archivo, datos, save=True)
            except Exception as e:
                print(f"Error procesando foto de perfil: {e}")
             
        
        return usuario
    

class UsuarioSerializerUpdate(serializers.ModelSerializer):
    foto_perfil = serializers.CharField(required=False, allow_blank=True)  

    class Meta:
        model = Usuario
        fields = ['nombre_usuario', 'email', 'bio', 'foto_perfil']  
        
    def update(self, instance, validated_data):
        # Actualizamos los campos básicos
        instance.nombre_usuario = validated_data.get('nombre_usuario', instance.nombre_usuario)
        instance.email = validated_data.get('email', instance.email)
        instance.bio = validated_data.get('bio', instance.bio)
        
       
        foto_base64 = validated_data.get('foto_perfil')
        if foto_base64:
            try:
                formato, imgstr = foto_base64.split(';base64,')
                ext = formato.split('/')[-1]
                datos = ContentFile(base64.b64decode(imgstr))
                file_name = f"fotos_perfil/{instance.nombre_usuario}_profile.{ext}"
                instance.foto_perfil.save(file_name, datos, save=True)
            except Exception as e:
                print(f"Error al procesar la foto: {e}")
        
        instance.save()
        return instance
    

class UsuarioSerializerActualizarNombre(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['nombre_usuario']
    
    def validate_nombre_usuario(self, nombre_usuario):
        usuario = Usuario.objects.filter(nombre_usuario=nombre_usuario).first()
        if usuario is not None and usuario.id != self.instance.id:
            raise serializers.ValidationError('Ya existe un usuario con ese nombre')
        return nombre_usuario
    

class AlbumSerializerCrear(serializers.ModelSerializer):
    portada = serializers.CharField(required=False, allow_blank=True) 
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())

    class Meta:
        model = Album
        fields = ['titulo', 'artista', 'usuario', 'portada', 'descripcion']

    def create(self, validated_data):
        portada_base64 = validated_data.pop('portada', None)
        

        album = Album.objects.create(**validated_data)

      
        if portada_base64:
            try:
                formato, imgstr = portada_base64.split(';base64,')
                ext = formato.split('/')[-1]
                
             
                datos = ContentFile(base64.b64decode(imgstr))
                
            
                nombre_archivo = f"album_portada_{album.id}.{ext}"
                album.portada.save(nombre_archivo, datos, save=True)
            except Exception as e:
                print(f"Error al procesar la portada: {e}")

        return album
    
    def update(self, instance, validated_data):
     
        instance.titulo = validated_data.get('titulo', instance.titulo)
        instance.artista = validated_data.get('artista', instance.artista)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)

       
        portada_base64 = validated_data.get('portada')
        if portada_base64:
            try:
                formato, imgstr = portada_base64.split(';base64,')
                ext = formato.split('/')[-1]
                datos = ContentFile(base64.b64decode(imgstr))
                nombre_archivo = f"album_portada_{instance.id}.{ext}"
                instance.portada.save(nombre_archivo, datos, save=True)
            except Exception as e:
                print(f"Error al procesar la portada: {e}")

        instance.save()
        return instance



class DetalleAlbumSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = DetalleAlbum
        fields = ['productor', 'estudio_grabacion', 'numero_pistas', 'sello_discografico', 'album']

    def validate_numero_pistas(self, value):
        if value <= 0:
            raise serializers.ValidationError("El número de pistas debe ser mayor que 0")
        return value

    def validate_productor(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre del productor debe tener al menos 3 caracteres")
        return value

    def create(self, validated_data):
        return DetalleAlbum.objects.create(**validated_data)



class AlbumSerializerTitulo(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['titulo']

    def validate_titulo(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El título debe tener al menos 3 caracteres")
        return value
    

class PlaylistSerializerCreate(serializers.ModelSerializer):
    canciones = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Cancion.objects.all()
    )

    class Meta:
        model = Playlist
        fields = ['nombre', 'descripcion', 'usuario', 'canciones', 'publica']

    def validate_nombre(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        return value

    def validate_descripcion(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres")
        return value

    def validate_canciones(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Debe seleccionar al menos una canción")
        return value

    def create(self, validated_data):
        canciones = validated_data.pop('canciones')
        playlist = Playlist.objects.create(**validated_data)
        for cancion in canciones:
            CancionPlaylist.objects.create(
                playlist=playlist,
                cancion=cancion,
                orden=list(canciones).index(cancion)
            )
        return playlist
    
class PlaylistSerializerUpdate(serializers.ModelSerializer):
    canciones = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Cancion.objects.all()
    )

    class Meta:
        model = Playlist
        fields = ['nombre', 'descripcion', 'canciones', 'publica']

    def validate_nombre(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("El nombre debe tener al menos 3 caracteres")
        return value

    def validate_descripcion(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres")
        return value

    def validate_canciones(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Debe seleccionar al menos una canción")
        return value

    def update(self, instance, validated_data):
        instance.nombre = validated_data.get('nombre', instance.nombre)
        instance.descripcion = validated_data.get('descripcion', instance.descripcion)
        instance.publica = validated_data.get('publica', instance.publica)
        
        # Actualizar canciones
        canciones = validated_data.get('canciones', None)
        if canciones is not None:
            instance.canciones.clear()
            instance.canciones.add(*canciones)

        instance.save()
        return instance
    

        
class PlaylistSerializerCanciones(serializers.ModelSerializer):
    canciones = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Cancion.objects.all()
    )

    class Meta:
        model = Playlist
        fields = ['canciones']

    def validate_canciones(self, value):
        if len(value) < 1:
            raise serializers.ValidationError("Debe seleccionar al menos una canción")
        return value

    def update(self, instance, validated_data):
        if 'canciones' in validated_data:
          
            # instance.canciones.clear()
 
            canciones = validated_data['canciones']
            for index, cancion in enumerate(canciones):
                CancionPlaylist.objects.create(
                    playlist=instance,
                    cancion=cancion,
                    orden=index
                )
        return instance
    


class LikeSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['usuario', 'cancion']

    def validate(self, data):
     
        if Like.objects.filter(
            usuario=data['usuario'],
            cancion=data['cancion']
        ).exists():
            raise serializers.ValidationError(
                "Este usuario ya dio like a esta canción"
            )
        return data












class CancionPlaylistSerializerMejorado(serializers.ModelSerializer):
    canciones = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )

    class Meta:
        model = CancionPlaylist
        fields = ['playlist', 'canciones']

    def validate(self, data):
        playlist = data['playlist']
        canciones = data['canciones']

        # Validar que no haya duplicados
        for cancion_id in canciones:
            if CancionPlaylist.objects.filter(
                playlist=playlist,
                cancion_id=cancion_id
            ).exists():
                raise serializers.ValidationError(
                    f"La canción {cancion_id} ya está en la playlist"
                )
        return data

    def create(self, validated_data):
        playlist = validated_data['playlist']
        canciones = validated_data.pop('canciones')
        
        # Crear las relaciones con orden automático
        cancion_playlists = []
        for index, cancion_id in enumerate(canciones):
            cancion_playlist = CancionPlaylist.objects.create(
                playlist=playlist,
                cancion_id=cancion_id,
                orden=index
            )
            cancion_playlists.append(cancion_playlist)
        
        return cancion_playlists[0] if cancion_playlists else None
