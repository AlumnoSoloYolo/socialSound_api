from django.shortcuts import render, redirect
from django.db.models import Sum, Q, Prefetch, Count
from .models import Usuario, Cliente, Moderador, Album, Cancion, Playlist, CancionPlaylist, Guardado, MensajePrivado, Like, Comentario, EstadisticasAlbum, DetalleAlbum
from django.views.defaults import page_not_found
from .forms import UsuarioModelForm, LoginForm, BusquedaAvanzadaUsuarioForm, AlbumModelForm, DetalleAlbumModelForm, BusquedaAvanzadaAlbumForm, ComentarioModelForm, BusquedaAvanzadaComentarioForm, CancionForm, DetallesCancionForm, BusquedaAvanzadaCancionForm, PlaylistForm, MensajePrivadoForm, BusquedaMensajesForm, UsuarioUpdateForm, BusquedaAvanzadaPlaylistForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required, permission_required
from datetime import date
from django.contrib.auth import logout
from django.db import transaction
from django.forms import formset_factory
from django.db.models import Max
from datetime import datetime
from django.contrib.auth.models import Group


## CRUD Usuario

def registro_usuario(request):
    datosFormulario = None
    mostrar_errores = False
    
    if request.method == "POST":
        datosFormulario = request.POST
        mostrar_errores = True
        
    form = UsuarioModelForm(datosFormulario, request.FILES)
    
    if request.method == "POST":
        usuario_creado = crear_usuario(form)
        if usuario_creado:
            messages.success(request, '¡Te has registrado con éxito!')
            return redirect('login_usuario')
        else:
            messages.error(request, 'Error al intentar registrarte')
            
    return render(request, 'CRUD_usuario/registro_usuario.html', {
        'form': form,
        'title': 'Registro de usuario',
        'mostrar_errores': mostrar_errores
    })

def crear_usuario(form):
    usuario_creado = False
    if form.is_valid():
        try:
            with transaction.atomic():
                usuario = form.save(commit=False)
                raw_password = form.cleaned_data.get('password')
                usuario.set_password(raw_password)
                
                if not usuario.foto_perfil:
                    usuario.foto_perfil = 'media/fotos_perfil/default_profile.png'
                    
                usuario.save()
                rol = int(form.cleaned_data.get('rol'))
                
                if rol == Usuario.CLIENTE:
                    grupo = Group.objects.get(name='Cliente') 
                    grupo.user_set.add(usuario)
                    cliente = Cliente.objects.create(
                        usuario=usuario,
                        genero_favorito=form.cleaned_data.get('genero_favorito'),
                        artista_favorito=form.cleaned_data.get('artista_favorito'),
                        acepta_terminos=form.cleaned_data.get('acepta_terminos')
                    )
                    cliente.save()
                elif rol == Usuario.MODERADOR:
                    grupo = Group.objects.get(name='Moderador') 
                    grupo.user_set.add(usuario)
                    moderador = Moderador.objects.create(
                        usuario=usuario,
                        experiencia_moderacion=form.cleaned_data.get('experiencia_moderacion'),
                        area_especialidad=form.cleaned_data.get('area_especialidad'),
                        codigo_moderador=form.cleaned_data.get('codigo_moderador')
                    )
                    moderador.save()
                    
                usuario_creado = True
        except Exception as error:
            print(error)
    
    return usuario_creado


def login_usuario(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            nombre_usuario = form.cleaned_data.get('nombre_usuario')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=nombre_usuario, password=password)

            if user is not None:
                login(request, user)
                
                request.session['ultima_conexion'] = timezone.now().strftime('%d/%m/%Y %H:%M')
                request.session['total_seguidores'] = user.obtener_seguidores().count()
                request.session['total_seguidos'] = user.obtener_seguidos().count()
                request.session['total_albumes'] = Album.objects.select_related('usuario').filter(usuario=user).count()
                
                messages.success(request, f'Bienvenido {user.nombre_usuario}', extra_tags='login')
                return redirect('index')
            else:
                messages.error(request, 'Credenciales inválidas', extra_tags='error_credencialess') 
    else:
        form = LoginForm()

    return render(request, 'CRUD_usuario/login_usuario.html', {'form': form})

@login_required
def logout_view(request):
    
    if 'ultima_conexion' in request.session:
        del request.session['ultima_conexion']
    if 'total_seguidores' in request.session:
        del request.session['total_seguidores']
    if 'total_seguidos' in request.session:
        del request.session['total_seguidos']
    if 'total_albumes' in request.session:
        del request.session['total_albumes']
        
    logout(request)
    return redirect('login_usuario')

@login_required
def actualizar_perfil(request, nombre_usuario):
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
    
    datosFormulario = None
    archivos = None
    
    if request.method == "POST":
        datosFormulario = request.POST
        archivos = request.FILES
    
    form = UsuarioUpdateForm(datosFormulario, archivos, instance=usuario)
    
    if request.method == "POST":
        if form.is_valid():
            try:
                usuario_actualizado = form.save()
                messages.success(request, f'Se ha actualizado el perfil de {usuario_actualizado.nombre_usuario} correctamente')
                return redirect('perfil_usuario', nombre_usuario=usuario_actualizado.nombre_usuario)
            except Exception as error:
                print(error)
                messages.error(request, 'Ha ocurrido un error al actualizar el perfil')
    
    return render(request, 'CRUD_usuario/actualizar_perfil.html', {
        "form": form,
        "usuario": usuario
    })

@login_required
@permission_required('socialSound.delete_usuario')
def eliminar_usuario(request, nombre_usuario):
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
    try:
        usuario.delete()
    except:
        pass
    return redirect('login_usuario')

@login_required
@login_required
def busqueda_avanzada_usuarios(request):
    form = BusquedaAvanzadaUsuarioForm(request.GET or None)
    
    # Iniciar el queryset base según el rol del usuario
    if request.user.rol == Usuario.MODERADOR:
        # Los moderadores pueden ver todos los usuarios
        usuarios = Usuario.objects.all().exclude(is_superuser=True)
    else:
        # Los clientes solo pueden ver otros clientes
         usuarios = Usuario.objects.filter(rol=Usuario.CLIENTE).exclude(is_superuser=True)

    filtros_aplicados = []

   
    if request.GET:
        if form.is_valid():
            if nombre_usuario := form.cleaned_data.get('nombre_usuario'):
                usuarios = usuarios.filter(nombre_usuario__icontains=nombre_usuario)
                filtros_aplicados.append(f"nombre: {nombre_usuario}")

            if ciudad := form.cleaned_data.get('ciudad'):
                usuarios = usuarios.filter(ciudad__icontains=ciudad)
                filtros_aplicados.append(f"Ciudad: {ciudad}")
            
            if edad_min := form.cleaned_data.get('edad_min'):
                fecha_max = date.today() - relativedelta(years=edad_min)
                usuarios = usuarios.filter(fecha_nac__lte=fecha_max)
                filtros_aplicados.append(f"Edad mínima: {edad_min} años")

            if edad_max := form.cleaned_data.get('edad_max'):
                fecha_min = date.today() - relativedelta(years=edad_max)
                usuarios = usuarios.filter(fecha_nac__gte=fecha_min)
                filtros_aplicados.append(f"Edad máxima: {edad_max} años")
            
            if bio := form.cleaned_data.get('bio_contains'):
                usuarios = usuarios.filter(bio__icontains=bio)
                filtros_aplicados.append(f"Biografía contiene: {bio}")
        else:
            filtros_aplicados.append("Error en los filtros ingresados")

    # Excluir al usuario actual de los resultados
    usuarios = usuarios.exclude(id=request.user.id)
    
    return render(request, 'CRUD_usuario/busqueda_avanzada_usuarios.html', {
        'form': form,
        'usuarios': usuarios,
        'filtros_aplicados': filtros_aplicados,
        'es_moderador': request.user.rol == Usuario.MODERADOR  
    })

@login_required
def seguir_usuario(request, usuario_id):
    usuario_a_seguir = Usuario.objects.get(id=usuario_id)
    request.user.seguir(usuario_a_seguir)
    return render(request, 'parciales/boton_seguir.html', {'usuario': usuario_a_seguir})

@login_required
def dejar_de_seguir_usuario(request, usuario_id):
    usuario_a_dejar = Usuario.objects.get(id=usuario_id)
    request.user.dejar_de_seguir(usuario_a_dejar)
    return render(request, 'parciales/boton_seguir.html', {'usuario': usuario_a_dejar})


### CRUD Álbum

@login_required
@permission_required('socialSound.add_album')
def crear_album(request, nombre_usuario):
    if request.user.nombre_usuario != nombre_usuario:
        return redirect('perfil_usuario', nombre_usuario=request.user.nombre_usuario)
    
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    album_form = AlbumModelForm(datosFormulario, request.FILES)
    detalle_form = DetalleAlbumModelForm(datosFormulario)
    
    if request.method == "POST":
        album_creado = crear_album_completo(album_form, detalle_form, request.user)
        if album_creado:
            messages.success(request, 'Álbum creado correctamente.')
            return redirect('perfil_usuario', nombre_usuario=request.user.nombre_usuario)
        else:
            messages.error(request, 'Error al crear el álbum')
            
    return render(request, 'CRUD_album/crear_album.html', {
        'album_form': album_form,
        'detalle_form': detalle_form,
        'title': 'Crear Nuevo Álbum',
        'operation': 'Crear'
    })

def crear_album_completo(album_form, detalle_form, usuario):
    album_creado = False
    if album_form.is_valid() and detalle_form.is_valid():
        try:
            with transaction.atomic():
                album = album_form.save(commit=False)
                album.usuario = usuario
                album.save()

                estadisticas_album = EstadisticasAlbum(album=album)
                estadisticas_album.save()

                detalle_album = detalle_form.save(commit=False)
                detalle_album.album = album
                detalle_album.save()
                
                album_creado = True
        except Exception as error:
            print(error)
    return album_creado



@login_required
@permission_required('socialSound.change_album')
def editar_album(request, nombre_usuario, album_id):
    
    album = Album.objects.select_related('detalle_album').get(id=album_id)
    detalle = album.detalle_album
  

    if request.method == 'POST':
       
        album_form = AlbumModelForm(request.POST, request.FILES, instance=album)
        detalle_form = DetalleAlbumModelForm(request.POST, instance=detalle)

        if album_form.is_valid() and detalle_form.is_valid():
           
            album_form.save()
            detalle_form.save()

            messages.success(request, 'Álbum actualizado correctamente')
            return redirect('perfil_usuario', nombre_usuario=request.user.nombre_usuario)
    else:
        album_form = AlbumModelForm(instance=album)
        detalle_form = DetalleAlbumModelForm(instance=detalle)

    return render(request, 'CRUD_album/editar_album.html', {
        'album_form': album_form,
        'detalle_form': detalle_form,
        'album': album,
        'nombre_usuario': nombre_usuario,
        'title': 'Editar Álbum',
        'operation': 'Actualizar'
    })




@login_required
def busqueda_avanzada_album(request):
    form = BusquedaAvanzadaAlbumForm(request.GET or None)
    
    # Ahora empezamos con todos los álbumes
    albums = Album.objects.all().select_related('usuario', 'detalle_album').order_by('-fecha_subida')
    filtros_aplicados = []

    if form.is_valid():
        if titulo := form.cleaned_data.get('titulo'):
            albums = albums.filter(titulo__icontains=titulo)
            filtros_aplicados.append(f"Título: {titulo}")
        
        if artista := form.cleaned_data.get('artista'):
            albums = albums.filter(artista__icontains=artista)
            filtros_aplicados.append(f"Artista: {artista}")
        
        if fecha_desde := form.cleaned_data.get('fecha_desde'):
            albums = albums.filter(fecha_subida__gte=fecha_desde)
            filtros_aplicados.append(f"fecha desde: {fecha_desde}")
        
        if fecha_hasta := form.cleaned_data.get('fecha_hasta'):
            albums = albums.filter(fecha_subida__lte=fecha_hasta)
            filtros_aplicados.append(f"fecha hasta: {fecha_hasta}")

    return render(request, "CRUD_album/busqueda_avanzada_albumes.html", {
        'form': form,
        'albums': albums,
        'filtros_aplicados': filtros_aplicados
    })





@login_required
@permission_required('socialSound.delete_album')
def eliminar_album(request, album_id):
   
    album = Album.objects.get(id=album_id)
    
    try:
        if request.method == 'POST':
           
            nombre_album = album.titulo
            album.delete()
            messages.success(request, f'El álbum "{nombre_album}" ha sido eliminado correctamente.')
    except:
        pass
    
    return redirect('perfil_usuario', nombre_usuario=request.user.nombre_usuario)

### CRUD cancion
@login_required
@permission_required('socialSound.add_album', 'socialSound.add_cancion')
def crear_album_con_canciones(request, nombre_usuario):
    if request.user.nombre_usuario != nombre_usuario:
        return redirect('perfil_usuario', nombre_usuario=request.user.nombre_usuario)

    CancionFormSet = formset_factory(CancionForm, extra=1, can_delete=True)
    DetallesCancionFormSet = formset_factory(DetallesCancionForm, extra=1, can_delete=True)

    if request.method == 'POST':
        album_form = AlbumModelForm(request.POST, request.FILES)
        detalle_album_form = DetalleAlbumModelForm(request.POST)
        cancion_formset = CancionFormSet(request.POST, request.FILES, prefix='canciones')
        detalles_cancion_formset = DetallesCancionFormSet(request.POST, prefix='detalles')

        if all([album_form.is_valid(), detalle_album_form.is_valid(), 
               cancion_formset.is_valid(), detalles_cancion_formset.is_valid()]):
            try:
                with transaction.atomic():

                    numero_pistas = sum(
                        1 for form in cancion_formset 
                        if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
                    )
                    album = album_form.save(commit=False)
                    album.usuario = request.user
                    album.save()

                    detalle_album = detalle_album_form.save(commit=False)
                    detalle_album.album = album
                    detalle_album.numero_pistas = numero_pistas 
                    detalle_album.save()

                    EstadisticasAlbum.objects.create(album=album)

                    for cancion_form, detalles_form in zip(cancion_formset, detalles_cancion_formset):
                        if cancion_form.cleaned_data and not cancion_form.cleaned_data.get('DELETE', False):
                            cancion = cancion_form.save(commit=False)
                            cancion.album = album
                            cancion.usuario = request.user
                            if not cancion_form.cleaned_data.get('portada'):
                                cancion.portada = album.portada
                            cancion.save()

                            detalles = detalles_form.save(commit=False)
                            detalles.cancion = cancion
                            detalles.duracion = cancion.obtener_duracion()
                            detalles.save()

                messages.success(request, 'Álbum y canciones creados exitosamente')
                return redirect('perfil_usuario', nombre_usuario=request.user.nombre_usuario)
            except Exception as e:
                messages.error(request, f'Error al crear el álbum: {str(e)}')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')

    else:
        album_form = AlbumModelForm()
        detalle_album_form = DetalleAlbumModelForm()
        cancion_formset = CancionFormSet(prefix='canciones')
        detalles_cancion_formset = DetallesCancionFormSet(prefix='detalles')

    context = {
        'album_form': album_form,
        'detalle_album_form': detalle_album_form,
        'cancion_formset': cancion_formset,
        'detalles_cancion_formset': detalles_cancion_formset,
        'title': 'Crear Nuevo Álbum'
       
    }
    return render(request, 'CRUD_album/crear_album_canciones.html', context)


@login_required
@permission_required('socialSound.change_cancion')
def editar_cancion(request, cancion_id):
    try:
        cancion = Cancion.objects.get(id=cancion_id)
        detalles = cancion.detalles
    except Cancion.DoesNotExist:
        messages.error(request, 'La canción no existe')
        return redirect('home') 
        
    datosCancion = None
    datosDetalles = None
    
    if request.method == "POST":
        datosCancion = request.POST
        datosDetalles = request.POST
        
    cancion_form = CancionForm(datosCancion, request.FILES if request.method == "POST" else None, instance=cancion)
    detalles_form = DetallesCancionForm(datosDetalles, instance=detalles)
    
    if request.method == "POST":
        if cancion_form.is_valid() and detalles_form.is_valid():
            try:
                cancion = cancion_form.save()
                detalles = detalles_form.save(commit=False)
                detalles.cancion = cancion
                detalles.save()
                
                messages.success(request, f'Se ha editado la canción {cancion.titulo} correctamente')
                return redirect('canciones_album', album_id=cancion.album.id)
                
            except Exception as error:
                print(error)  
                messages.error(request, 'Ha ocurrido un error al guardar la canción')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')
    
    return render(request, 'CRUD_cancion/editar_cancion.html', {
        'cancion_form': cancion_form,
        'detalles_form': detalles_form,
        'cancion': cancion,
        'title': f'Editar Canción: {cancion.titulo}'
    })

@login_required
@permission_required('socialSound.delete_cancion')
def eliminar_cancion(request, cancion_id):
    cancion = Cancion.objects.get(id=cancion_id)
    album_id = cancion.album.id
    try:
        cancion.delete()
        messages.success(request, 'Canción eliminada con éxito')
    except:
        pass

    return redirect('canciones_album', album_id=album_id)


@login_required
@permission_required('socialSound.add_cancion')
def agregar_cancion_album(request, album_id):
    album = Album.objects.get(id=album_id)
    
    if request.method == 'POST':
        cancion_form = CancionForm(request.POST, request.FILES)
        detalles_form = DetallesCancionForm(request.POST)
        
        if cancion_form.is_valid() and detalles_form.is_valid():
            cancion = cancion_form.save(commit=False)
            cancion.album = album
            cancion.usuario = request.user
            if not cancion_form.cleaned_data.get('portada'):
                cancion.portada = album.portada
            cancion.save()

            detalles = detalles_form.save(commit=False)
            detalles.cancion = cancion
            detalles.save()

            messages.success(request, 'Canción agregada exitosamente al álbum')
            return redirect('canciones_album', album_id=album.id)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')
    else:
        cancion_form = CancionForm()
        detalles_form = DetallesCancionForm()

    return render(request, 'CRUD_cancion/agregar_cancion.html', {
        'cancion_form': cancion_form,
        'detalles_form': detalles_form,
        'album': album,
        'title': f'Añadir canción al álbum {album.titulo}'
    })

def busqueda_avanzada_canciones(request):
    form = BusquedaAvanzadaCancionForm(request.GET or None)

    canciones = Cancion.objects.all()

    if form.is_valid():
        if titulo := form.cleaned_data.get('titulo'):
            canciones = canciones.filter(titulo__icontains=titulo)
        if artista := form.cleaned_data.get('artista'):
            canciones = canciones.filter(artista__icontains=artista)
        if fecha_desde := form.cleaned_data.get('fecha_desde'):
            canciones = canciones.filter(fecha_subida__gte=fecha_desde)
        if fecha_hasta := form.cleaned_data.get('fecha_hasta'):
            canciones = canciones.filter(fecha_subida__lte=fecha_hasta)
        
        if album := form.cleaned_data.get('album'):
            canciones = canciones.filter(album__titulo__icontains=album)
  
    return render(request, 'CRUD_cancion/busqueda_avanzada_canciones.html', {
        'form': form,
        'canciones': canciones,
        'title': 'Búsqueda Avanzada de Canciones',
        'is_adding_to_playlist': True if request.GET.get('mode') == 'playlist' else False
    })



### CRUD Comentario
@login_required
@permission_required('socialSound.add_comentario')
def crear_comentario(request, album_id):
    album = Album.objects.get(id=album_id)
    
    datosFormulario = None
    if request.method == "POST":
        datosFormulario = request.POST
        
    form = ComentarioModelForm(datosFormulario)
    
    if request.method == "POST":
        comentario_creado = crear_comentario_album(form, request.user, album)
        if comentario_creado:
            messages.success(request, 'Tu comentario se ha publicado con éxito')
            return redirect('comentarios_album', album_id=album.id)
        else:
            messages.error(request, 'Hubo un error al publicar tu comentario')

    comentarios = Comentario.objects.filter(album=album).order_by('-fecha_publicacion')
    
    return render(request, 'album/comentarios_album.html', {
        'form': form,
        'album': album,
        'comentarios': comentarios
    })

def crear_comentario_album(form, usuario, album):
    comentario_creado = False
    if form.is_valid():
        try:
            comentario = form.save(commit=False)
            comentario.usuario = usuario
            comentario.album = album
            comentario.save()
            comentario_creado = True
        except Exception as error:
            print(error)
    return comentario_creado


@login_required
@permission_required('socialSound.change_comentario')
def actualizar_comentario(request, album_id, comentario_id):
    try:
        album = Album.objects.get(id=album_id)
        comentario = Comentario.objects.get(id=comentario_id)
    except Album.DoesNotExist:
        messages.error(request, 'El álbum no existe')
        return redirect('home') 
   
    
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = ComentarioModelForm(datosFormulario, instance=comentario)
    
    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Se ha actualizado el comentario correctamente')
                return redirect('comentarios_album', album_id=album.id)
            except Exception as error:
                print(error)  
                messages.error(request, 'Ha ocurrido un error al actualizar el comentario')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')

    return render(request, 'CRUD_comentario/editar_comentario.html',  {
        'form': formulario,
        'album': album,
        'comentario': comentario,
        'is_update': True
    })
    

def busqueda_avanzada_comentarios(request, album_id):
    album = Album.objects.get(id=album_id)
    form_busqueda = BusquedaAvanzadaComentarioForm(request.GET or None)
    
    comentarios = Comentario.objects.filter(album=album).select_related('usuario')
    
    if form_busqueda.is_valid():
        contenido = form_busqueda.cleaned_data.get('contenido')
        usuario = form_busqueda.cleaned_data.get('usuario')
        fecha_desde = form_busqueda.cleaned_data.get('fecha_desde')
        fecha_hasta = form_busqueda.cleaned_data.get('fecha_hasta')
        
        if contenido:
            comentarios = comentarios.filter(contenido__icontains=contenido)
        
        if usuario:
            comentarios = comentarios.filter(usuario__nombre_usuario__icontains=usuario)
        
        if fecha_desde:
            comentarios = comentarios.filter(fecha_publicacion__date__gte=fecha_desde)
        
        if fecha_hasta:
            comentarios = comentarios.filter(fecha_publicacion__date__lte=fecha_hasta)
    
    comentarios = comentarios.order_by('-fecha_publicacion')
    
    context = {
        'album': album,
        'comentarios': comentarios,
        'form_busqueda': form_busqueda
    }
    
    if request.headers.get('HX-Request'):
        return render(request, 'comentarios/includes/lista_comentarios.html', context)
    
    return render(request, 'comentarios/includes/busqueda_avanzada.html', context)


@login_required
@permission_required('socialSound.delete_comentario')
def eliminar_comentario(request, album_id, comentario_id):
    comentario = Comentario.objects.get(id=comentario_id, album_id=album_id)
   
    comentario.delete()
       
    return redirect('comentarios_album', album_id=album_id)


## CRUD playlists
@login_required
@permission_required('socialSound.add_playlist')
def crear_playlist_usuario(form, usuario):
   
    try:
        if form.is_valid():
            # Crear la playlist sin guardar aún
            playlist = form.save(commit=False)
            playlist.usuario = usuario
            playlist.save()
            
            # Guardar las canciones seleccionadas con su orden
            canciones = form.cleaned_data.get('canciones', [])
            for index, cancion in enumerate(canciones):
                CancionPlaylist.objects.create(
                    playlist=playlist,
                    cancion=cancion,
                    orden=index
                )
            
            return True
        return False
    except Exception as e:
        print(f"Error al crear playlist: {str(e)}")
        return False

@login_required
@permission_required('socialSound.add_playlist')
def crear_playlist(request):
    if request.method == "POST":
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.usuario = request.user
            playlist.save()
            form.save_m2m()
            messages.success(request, 'Playlist creada exitosamente')
            return redirect('lista_playlist', nombre_usuario=request.user.nombre_usuario)
        else:
            messages.error(request, 'Error al crear la playlist. Por favor verifica los datos ingresados.')
    else:
        form = PlaylistForm()

    return render(request, 'CRUD_playlist/crear_playlist.html', {
        'form': form,
        'title': 'Crear Nueva Playlist'
    })
@login_required
@permission_required('socialSound.change_playlist')
def editar_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    
    if request.method == "POST":
        formulario = PlaylistForm(request.POST, instance=playlist)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, f'Se ha editado la playlist {formulario.cleaned_data.get("nombre")} correctamente')
            return redirect('lista_playlist', nombre_usuario=playlist.usuario.nombre_usuario)
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')
    else:
        formulario = PlaylistForm(instance=playlist)

    return render(request, 'CRUD_playlist/editar_playlist.html', {
        'form': formulario,
        'title': 'Editar Playlist'
    })

@login_required
def busqueda_avanzada_playlists(request):
    form = BusquedaAvanzadaPlaylistForm(request.GET or None)
    
    playlists = Playlist.objects.all()
    
    if form.is_valid():
        if nombre := form.cleaned_data.get('nombre'):
            playlists = playlists.filter(nombre__icontains=nombre)
        
        if usuario := form.cleaned_data.get('usuario'):
            playlists = playlists.filter(usuario__nombre_usuario__icontains=usuario)
            
        if fecha_desde := form.cleaned_data.get('fecha_desde'):
            playlists = playlists.filter(fecha_creacion__gte=fecha_desde)
            
        if fecha_hasta := form.cleaned_data.get('fecha_hasta'):
            playlists = playlists.filter(fecha_creacion__lte=fecha_hasta)
            
        if (publica := form.cleaned_data.get('publica')) in ['True', 'False']:
            playlists = playlists.filter(publica=publica == 'True')
    
    return render(request, 'CRUD_playlist/busqueda_avanzada_playlists.html', {
        'form': form,
        'playlists': playlists,
        'title': 'Búsqueda Avanzada de Playlists'
    })


@login_required
@permission_required('socialSound.add_cancion')
def agregar_cancion_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    
    if request.method == 'POST':
        form_busqueda = BusquedaAvanzadaCancionForm(request.POST)
        if form_busqueda.is_valid():
            canciones = busqueda_avanzada_canciones(form_busqueda.cleaned_data)
        else:
            canciones = Cancion.objects.all()
        
        cancion_id = request.POST.get('cancion_id')
        if cancion_id:
            cancion = Cancion.objects.get(id=cancion_id)
            if not CancionPlaylist.objects.filter(playlist=playlist, cancion=cancion).exists():
                CancionPlaylist.objects.create(playlist=playlist, cancion=cancion)
            return redirect('canciones_playlist', playlist_id=playlist.id)
    else:
        form_busqueda = BusquedaAvanzadaCancionForm()
        canciones = Cancion.objects.all()
    
    return render(request, 'CRUD_playlist/agregar_cancion.html', {
        'playlist': playlist,
        'canciones': canciones,
        'form_busqueda': form_busqueda,
    })

@login_required
@permission_required('socialSound.add_mensajeprivado')
def crear_mensaje_privado(request, usuario_id):
    try:
        otro_usuario = Usuario.objects.get(id=usuario_id)
        mensajes = MensajePrivado.objects.filter(
            Q(emisor=request.user, receptor=otro_usuario) |
            Q(emisor=otro_usuario, receptor=request.user)
        ).order_by('fecha_envio')

        datosFormulario = None
        if request.method == "POST":
            datosFormulario = request.POST
            
        form = MensajePrivadoForm(datosFormulario, user=request.user)
        
        if request.method == "POST" and 'enviar_mensaje' in request.POST:
            try:
                mensaje_creado = crear_mensaje(form, request.user, otro_usuario)
                if mensaje_creado:
                    messages.success(request, "Mensaje enviado correctamente")
                    return redirect('chat', usuario_id=usuario_id)
                else:
                    messages.error(request, "Por favor, corrija los errores en el formulario")
            except Exception as error:
                print(error)  
                messages.error(request, "Error al enviar el mensaje")

        return render(request, 'CRUD_mensajePrivado/crear_chat.html', {
            'mensajes': mensajes,
            'otro_usuario': otro_usuario,
            'form': form
        })
    except Usuario.DoesNotExist:
        messages.error(request, "El usuario no existe")
        return redirect('home')

@login_required
@permission_required('socialSound.add_mensajeprivado')
def crear_mensaje(form, emisor, receptor):
    if form.is_valid():
        try:
            mensaje = form.save(commit=False)
            mensaje.emisor = emisor
            mensaje.receptor = receptor
            mensaje.save()
            return True
        except Exception as error:
            print(error)  
            return False
    return False


## busqued avanzada de mensajes que he implementado en el template de listas de chats
def lista_chats(request):
    form = BusquedaMensajesForm(request.GET or None)
    
    # Query base usando las relaciones correctas: emisor y receptor
    usuarios = Usuario.objects.filter(
        Q(emisor__receptor=request.user) |  # Usuarios que me han enviado mensajes
        Q(receptor__emisor=request.user)    # Usuarios a los que he enviado mensajes
    ).distinct()

    if form.is_valid():

        if form.cleaned_data.get('contenido'):
            usuarios = usuarios.filter(
                Q(emisor__contenido__icontains=form.cleaned_data['contenido']) |
                Q(receptor__contenido__icontains=form.cleaned_data['contenido'])
            )

        if form.cleaned_data.get('usuario'):
            usuarios = usuarios.filter(
                nombre_usuario__icontains=form.cleaned_data['usuario']
            )

        if form.cleaned_data.get('fecha_desde'):
            usuarios = usuarios.filter(
                Q(emisor__fecha_envio__date__gte=form.cleaned_data['fecha_desde']) |
                Q(receptor__fecha_envio__date__gte=form.cleaned_data['fecha_desde'])
            )

        if form.cleaned_data.get('fecha_hasta'):
            usuarios = usuarios.filter(
                Q(emisor__fecha_envio__date__lte=form.cleaned_data['fecha_hasta']) |
                Q(receptor__fecha_envio__date__lte=form.cleaned_data['fecha_hasta'])
            )

    usuarios = usuarios.annotate(
        ultima_fecha=Max('emisor__fecha_envio') 
    ).order_by('-ultima_fecha')

  
    mensajes = Prefetch(
        'emisor',
        queryset=MensajePrivado.objects.filter(
            Q(receptor=request.user) |
            Q(emisor=request.user)
        ).order_by('-fecha_envio')[:1],
        to_attr='ultimo_mensaje'
    )
    usuarios = usuarios.prefetch_related(mensajes)

    return render(request, 'CRUD_mensajePrivado/lista_chats.html', {
        'form': form,
        'usuarios': usuarios,
    })


@login_required
@permission_required('socialSound.change_mensajeprivado')
def editar_mensaje(request, mensaje_id):
  
    mensaje = MensajePrivado.objects.get(id=mensaje_id)

    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = MensajePrivadoForm(datosFormulario, instance=mensaje)
    
    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, 'Se ha editado el mensaje correctamente')
                return redirect('chat', usuario_id=mensaje.receptor.id)
            except Exception as error:
                print(error) 
                messages.error(request, 'Ha ocurrido un error al actualizar el mensaje')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario')
    

    return render(request, 'CRUD_mensajePrivado/editar_mensaje.html', {
        'form': formulario,
        'mensaje': mensaje,
    })

@login_required
@permission_required('socialSound.delete_mensajeprivado')
def eliminar_mensaje(request, mensaje_id):
    mensaje = MensajePrivado.objects.get(id=mensaje_id)
    
    # Si es moderador, necesitamos identificar el contexto del chat
    if request.user.rol == 2:
        # Si el moderador está viendo el chat entre emisor y receptor,
        # queremos mantener ese contexto
        chat_usuario_id = mensaje.emisor.id if request.user == mensaje.receptor else mensaje.receptor.id
    else:
        # Para usuarios normales, vamos al chat con el receptor
        chat_usuario_id = mensaje.receptor.id

    # Verificar si el usuario puede eliminar el mensaje
    if request.user == mensaje.emisor or request.user.rol == 2:
        try:
            mensaje.delete()
            messages.success(request, "Se ha eliminado el mensaje correctamente")
        except Exception as e:
            messages.error(request, "Error al eliminar el mensaje")
            print(f"Error al eliminar mensaje: {e}")
    
    return redirect('chat', usuario_id=chat_usuario_id)



@login_required
@permission_required('socialSound.delete_playlist')
def eliminar_playlist(request, playlist_id):
    playlist = Playlist.objects.get(id=playlist_id)
    playlist_owner = playlist.usuario
   
    try:
        playlist.delete()
        messages.success(request, "Se ha eliminado la playlist correctamente")
    except:
        pass
            
       
    else:
        
        return redirect('lista_playlist', nombre_usuario=playlist_owner.nombre_usuario)











































# 1. Página de inicio con enlaces a todas las URLs
@login_required
def index(request):
    
    if(not 'fecha_inicio' in request.session):
        request.session['fecha_inicio'] = datetime.now().strftime('%d/%m/%Y %H:%M')
        
    # Renderiza la plantilla principal con enlaces a las demás páginas de la aplicación
    return render(request, "index.html")


# 2. Mostrar el perfil del usuario
@login_required
def perfil_usuario(request, nombre_usuario):
    # Obtenemos el usuario por nombre de usuario
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)

    # Llamamos a los métodos de seguidos y seguidores para acceder a ellos por separado
    seguidos = usuario.obtener_seguidos()
    total_seguidos = seguidos.count()
    seguidores = usuario.obtener_seguidores()
    total_seguidores = seguidores.count()

    # Obtenemos todos los álbumes del usuario
    albumes = Album.objects.select_related('usuario').filter(usuario=usuario)
    total_albumes = albumes.count()  # Contar el total de álbumes

    # Renderizamos la plantilla con los datos del perfil y estadísticas
    return render(request, 'usuario/perfil_usuario.html', 
                  {
                      'usuario': usuario,
                      'seguidos': seguidos,
                      'seguidores': seguidores,
                      'albumes': albumes,
                      'total_seguidos': total_seguidos,
                      'total_seguidores': total_seguidores,
                      'total_albumes': total_albumes
                  })



@login_required
def feed(request):
      # Obtener los usuarios que sigue el usuario actual
    usuarios_seguidos = request.user.obtener_seguidos()
    
    # Obtener los álbumes solo de los usuarios seguidos
    albums = Album.objects.filter(
        usuario__in=usuarios_seguidos
    ).select_related('usuario', 'detalle_album').order_by('-fecha_subida')

    return render(request, "usuario/feed.html", {
        'albums': albums
    })


# 4. Listar álbumes de un usuario específico
def lista_albumes(request, nombre_usuario):
    # Primero obtenemos el usuario y sus álbumes
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
    albumes = Album.objects.filter(usuario=usuario).order_by('fecha_subida').select_related('usuario', 'album').prefetch_related('canciones')

    # Renderizamos la lista de álbumes del usuario
    return render(request, 'album/lista_albumes.html', {'albumes': albumes})


# 5. Detalles de un álbum específico
def detalle_album(request, album_id):
    # Obtenemos el álbum, usuario y detalles del album por separado
    album = Album.objects.get(id=album_id)
    usuario = album.usuario
    detalles_album = album.detalle_album # Información detallada del álbum (OneToOne)
    estadisticas_album = album.estadisticasalbum  # Estadísticas del álbum (OneToOne)

    # Renderizamos plantilla con los detalles del álbum y las estadísticas
    return render(request, 'album/detalle_album.html', {
        'album': album,
        'detalles_album': detalles_album,
        'estadisticas_album': estadisticas_album,
        'usuario': usuario
    })


# 6. Listar canciones de un álbum específico
def canciones_album(request, album_id):
    # Obtenemos el álbum y sus canciones
    album = Album.objects.select_related('usuario').prefetch_related(Prefetch('canciones')).get(id=album_id)

    # Renderizamos la plantilla de canciones para el álbum
    return render(request, 'cancion/canciones_album.html', {'album': album})


# 7. Comentarios de un álbum específico
def comentarios_album(request, album_id):
    album = Album.objects.get(id=album_id)
    
    # Inicializamos el formulario con los datos de GET si existen
    form_busqueda = BusquedaAvanzadaComentarioForm(request.GET or None)
    
    # Obtenemos los comentarios base
    comentarios = Comentario.objects.filter(album=album).select_related('usuario')
    
    # Si el formulario se envía y es válido, aplicamos los filtros
    if form_busqueda.is_valid():
        contenido = form_busqueda.cleaned_data.get('contenido')
        usuario = form_busqueda.cleaned_data.get('usuario')
        fecha_desde = form_busqueda.cleaned_data.get('fecha_desde')
        fecha_hasta = form_busqueda.cleaned_data.get('fecha_hasta')
        
        if contenido:
            comentarios = comentarios.filter(contenido__icontains=contenido)
        
        if usuario:
            comentarios = comentarios.filter(usuario__nombre_usuario__icontains=usuario)
        
        if fecha_desde:
            comentarios = comentarios.filter(fecha_publicacion__date__gte=fecha_desde)
        
        if fecha_hasta:
            comentarios = comentarios.filter(fecha_publicacion__date__lte=fecha_hasta)
    
    comentarios = comentarios.order_by('-fecha_publicacion')

    return render(request, 'album/comentarios_album.html', {
        'album': album,
        'comentarios': comentarios,
        'form_busqueda': form_busqueda,
        'form': ComentarioModelForm()  # Añadimos el formulario de crear comentario
    })


# 8. Detalles de una canción específica
def detalle_cancion(request, cancion_id):
    # Obtenemos la canción, sus detalles y su álbum
    cancion = Cancion.objects.get(id=cancion_id)
    detalles_cancion = cancion.detalles  # Detalles adicionales (OneToOne)
    album = cancion.album  # Álbum al que pertenece la canción

    # Rnederizamos la plantilla con los detalles de la canción
    return render(request, 'cancion/detalle_cancion.html', 
                  { 
                      'cancion': cancion,
                      'detalles': detalles_cancion, 
                      'album': album,
                  })


# 9. Listar las playlists creadas por un usuario
def lista_playlist(request, nombre_usuario):
    # Obtenemos el usuario ysus playlists
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
    playlists = Playlist.objects.filter(usuario=usuario)

    # Renderizamos la plantilla con la lista de playlists del usuario
    return render(request, 'playlist/lista_playlist.html', {'playlists': playlists, 'usuario': usuario})


# 10. Contenido de una playlist específica
def canciones_playlist(request, playlist_id):
    # Obtenemos la playlist y sus canciones, además de los likes por cada canción
    playlist = Playlist.objects.select_related('usuario').prefetch_related('canciones').prefetch_related('canciones__like_set__usuario').get(id=playlist_id)

    # Renderizamos la plantilla con las canciones de la playlist
    return render(request, 'cancion/canciones_playlist.html', {
        'playlist': playlist,
    })


# 11. Lista de canciones guardadas por el usuario
def canciones_guardadas(request, nombre_usuario):
    # Obtenemos el usuario y las canciones guardadas
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
    lista_canciones = Guardado.objects.filter(usuario=usuario).select_related('cancion', 'cancion__usuario')

    # Renderizamos la plantilla con las canciones guardadas
    return render(request, 'cancion/canciones_guardadas.html', {
        'usuario': usuario,
        'lista_canciones': lista_canciones,
    })


# 12. Interfaz de mensajes privados entre dos usuarios
def mensajes_privados(request, emisor_id, receptor_id):
    # Los primero que he hecho ha sido obtener los usuarios que participan en la conversación
    emisor = Usuario.objects.get(id=emisor_id)
    receptor = Usuario.objects.get(id=receptor_id)

    # Filtramos mensajes entre el emisor y el receptor
    mensajes = MensajePrivado.objects.filter(
        Q(emisor_id=emisor_id, receptor_id=receptor_id) | 
        Q(emisor_id=receptor_id, receptor_id=emisor_id)
    ).select_related('emisor', 'receptor').order_by('fecha_envio')

    # Si se envía un nuevo mensaje 
    if request.method == "POST":
        contenido = request.POST.get('contenido')
        if contenido: 
            nuevo_mensaje = MensajePrivado(
                emisor=emisor,
                receptor=receptor,
                contenido=contenido
            )
            nuevo_mensaje.save()  # Guardamos el nuevo mensaje en la base de datos
            return redirect('mensajes_privados', emisor_id=emisor_id, receptor_id=receptor_id)

    # Renderizamos la plantilla con los mensajes entre los dos usuarios
    return render(request, 'usuario/mensajes_privados.html', {
        'mensajes': mensajes,
        'emisor': emisor,
        'receptor': receptor
    })


# 13 listar usuarios que un usuario específico no sigue
def lista_no_sigue(request, nombre_usuario):
    # Obtenemos el usuario actual
    usuario_actual = Usuario.objects.get(nombre_usuario=nombre_usuario)
    # Obtener todos los usuarios que no son el actual
    todos_usuarios = Usuario.objects.exclude(id=usuario_actual.id)
    
    # Filtramos usuarios que no están en la relación 'seguidores' del usuario actual
    # Aplicamos el filtro para obtener usuarios que el usuario actual NO sigue.
    usuarios_no_seguidos = todos_usuarios.filter(seguidores__isnull=True)

    return render(request, 'usuario/lista_no_sigue.html', {
        'usuarios_no_seguidos': usuarios_no_seguidos
    })



def lista_seguidores(request, nombre_usuario):
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
    usuarios_seguidores = usuario.obtener_seguidores()
    return render(request, 'usuario/usuarios_seguidores.html', {
        'usuarios_seguidores': usuarios_seguidores,
        'usuario_perfil': usuario
    })

def lista_seguidos(request, nombre_usuario):
    usuario = Usuario.objects.get(nombre_usuario=nombre_usuario)
    usuarios_seguidos = usuario.obtener_seguidos()
    return render(request, 'usuario/usuarios_seguidos.html', {
        'usuarios_seguidos': usuarios_seguidos,
        'usuario_perfil': usuario
    })

#Vistas de error
def mi_error_400(request,exception=None):
    return render(request, 'errores/400.html',None,None,400)

def mi_error_403(request,exception=None):
    return render(request, 'errores/403.html',None,None,403)

def mi_error_404(request,exception=None):
    return render(request, 'errores/404.html',None,None,404)

def mi_error_500(request,exception=None):
    return render(request, 'errores/500.html',None,None,500)
