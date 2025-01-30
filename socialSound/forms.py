from django.forms import ModelForm
from django import forms
from .models import Usuario, Album, DetalleAlbum, Comentario, Cancion, DetallesCancion, Playlist, MensajePrivado
from datetime import date
import re
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.forms import SetPasswordForm


class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        
        # Check password length
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        # Check for at least one digit
        if not re.search(r'\d', password):
            raise forms.ValidationError("Password must contain at least one number.")
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise forms.ValidationError("Password must contain at least one special character.")
        
        return password
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
       
        self.fields['new_password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Nueva contraseña'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirmar nueva contraseña'
        })


class UsuarioModelForm(ModelForm):
    # Campos originales
    email = forms.CharField(
        required=False,  
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    nombre_usuario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    rol = forms.ChoiceField(
        choices=Usuario.ROLES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Nuevos campos para Cliente
    genero_favorito = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    artista_favorito = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    acepta_terminos = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    # Nuevos campos para Moderador
    experiencia_moderacion = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    area_especialidad = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    codigo_moderador = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['email', 'nombre_usuario', 'password', 'bio', 'ciudad', 'fecha_nac', 'foto_perfil', 'rol']
        labels = '__all__'
        help_texts = {
            'email': '100 caracteres como máximo',
            'nombre_usuario': '100 caracteres como máximo',
            'password': 'Debe contener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial',
            'ciudad': '150 caracteres como máximo'
        }
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe aquí tu descripción...',
                'rows': 4,
                'cols': 50
            }),
            'fecha_nac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()

        # Validaciones originales
        # Email
        email = cleaned_data.get('email', '')
        if not email.strip():
            self.add_error('email', 'Este campo es requerido.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email', 'Introduce un correo electrónico válido.')
        
        # Validación del nombre de usuario
        nombre_usuario = cleaned_data.get('nombre_usuario', '')
        if not nombre_usuario.strip():
            self.add_error('nombre_usuario', 'Este campo es requerido.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', nombre_usuario):
            self.add_error('nombre_usuario', 'El nombre de usuario solo puede contener letras, números y guiones bajos')
        elif Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            if not self.instance.pk or (self.instance.pk and self.instance.nombre_usuario != nombre_usuario):
                self.add_error('nombre_usuario', 'Nombre de usuario en uso')
        
        # Validación de la contraseña
        password = cleaned_data.get('password', '')
        if not password.strip():
            self.add_error('password', 'Este campo es requerido.')
        elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            self.add_error('password', 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial (@$!%*?&)')

        # Validaciones específicas según el rol
        rol = cleaned_data.get('rol')

        if rol == str(Usuario.CLIENTE):
            # Validaciones para Cliente
            if not cleaned_data.get('acepta_terminos'):
                self.add_error('acepta_terminos', 'Debes aceptar los términos y condiciones')
                
        elif rol == str(Usuario.MODERADOR):
            # Validaciones para Moderador
            codigo = cleaned_data.get('codigo_moderador')
            if not codigo:
                self.add_error('codigo_moderador', 'El código de moderador es obligatorio')
            elif not codigo.startswith('MOD-'):
                self.add_error('codigo_moderador', 'El código debe empezar con "MOD-"')
                
            experiencia = cleaned_data.get('experiencia_moderacion')
            if not experiencia:
                self.add_error('experiencia_moderacion', 'La experiencia es obligatoria')
            elif experiencia < 1:
                self.add_error('experiencia_moderacion', 'Debes tener al menos 1 año de experiencia')

            area = cleaned_data.get('area_especialidad')
            if not area:
                self.add_error('area_especialidad', 'El área de especialidad es obligatoria')
            
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer campos condicionales según el rol
        if 'data' in kwargs:
            rol = kwargs['data'].get('rol')
            if rol == str(Usuario.CLIENTE):
                self.fields['codigo_moderador'].widget = forms.HiddenInput()
                self.fields['experiencia_moderacion'].widget = forms.HiddenInput()
                self.fields['area_especialidad'].widget = forms.HiddenInput()
            elif rol == str(Usuario.MODERADOR):
                self.fields['genero_favorito'].widget = forms.HiddenInput()
                self.fields['artista_favorito'].widget = forms.HiddenInput()
                self.fields['acepta_terminos'].widget = forms.HiddenInput()

    def save(self, commit=True):
        user = super().save(commit=False)
        if 'password' in self.cleaned_data and self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user
    
class LoginForm(forms.Form):
    nombre_usuario = forms.CharField(
        required=True,
        label='Nombre de usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu nombre de usuario'
        })
    )
    password = forms.CharField(
        required=True,
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu contraseña'
        })
    )

    def clean(self):
        super().clean()
        nombre_usuario = self.cleaned_data.get('nombre_usuario')
        password = self.cleaned_data.get('password')

        if nombre_usuario and password:
            try:
                user = Usuario.objects.get(nombre_usuario=nombre_usuario)
                if not user.check_password(password):
                    self.add_error('password', 'Contraseña incorrecta')
            except Usuario.DoesNotExist:
                self.add_error('nombre_usuario', 'Usuario no encontrado')

        return self.cleaned_data


class UsuarioUpdateForm(ModelForm):
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    nombre_usuario = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text='Dejar vacío si no desea cambiar la contraseña'
    )

    class Meta:
        model = Usuario
        fields = ['email', 'nombre_usuario', 'bio', 'ciudad', 'fecha_nac', 'foto_perfil']
        labels = '__all__'
        help_texts = {
            'email': '100 caracteres como máximo',
            'nombre_usuario': '100 caracteres como máximo',
            'ciudad': '150 caracteres como máximo'
        }
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe aquí tu descripción...',
                'rows': 4,
                'cols': 50
            }),
            'fecha_nac': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'foto_perfil': forms.FileInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()

        # Email
        email = cleaned_data.get('email', '')
        if not email.strip():
            self.add_error('email', 'Este campo es requerido.')
        elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            self.add_error('email', 'Introduce un correo electrónico válido.')
        
        # Validación del nombre de usuario
        nombre_usuario = cleaned_data.get('nombre_usuario', '')
        if not nombre_usuario.strip():
            self.add_error('nombre_usuario', 'Este campo es requerido.')
        elif not re.match(r'^[a-zA-Z0-9_]+$', nombre_usuario):
            self.add_error('nombre_usuario', 'El nombre de usuario solo puede contener letras, números y guiones bajos')
        elif Usuario.objects.filter(nombre_usuario=nombre_usuario).exists():
            if not self.instance.pk or (self.instance.pk and self.instance.nombre_usuario != nombre_usuario):
                self.add_error('nombre_usuario', 'Nombre de usuario en uso')
            
        return cleaned_data
    


class BusquedaAvanzadaUsuarioForm(forms.Form):
    nombre_usuario = forms.CharField(
        label='Nombre usuario',
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar usuario por nombre...'
        })
    )
    ciudad = forms.CharField(
        label='Ciudad',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por ciudad...'
        })
    )
    edad_min = forms.IntegerField(
        label='Edad mínima',
        required=False,
        min_value=1,  
        max_value=120,  
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Edad mínima...'
        })
    )
    edad_max = forms.IntegerField(
        label='Edad máxima',
        required=False,
        min_value=1,
        max_value=120,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Edad máxima...'
        })
    )
    bio_contains = forms.CharField(
        label='Buscar según biografía',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en la biografía'
        })
    )

    def clean(self):
        cleaned_data = super().clean()

        # Verificar que al menos un campo tiene valor
        if not any(cleaned_data.values()):
            raise forms.ValidationError("Debes especificar al menos un criterio de búsqueda")

        edad_min = cleaned_data.get('edad_min')
        edad_max = cleaned_data.get('edad_max')

        # Si se especifica solo una edad, usar la misma para ambos límites
        if edad_min and not edad_max:
            cleaned_data['edad_max'] = edad_min
        elif edad_max and not edad_min:
            cleaned_data['edad_min'] = edad_max

        # Si ambas edades están especificadas, verificar que min <= max
        if edad_min and edad_max and edad_min > edad_max:
            raise forms.ValidationError("La edad mínima no puede ser mayor que la edad máxima")

        # Convertir edades a fechas para la búsqueda
        if edad_min:
            cleaned_data['fecha_max'] = date.today().replace(year=date.today().year - edad_min)
        if edad_max:
            cleaned_data['fecha_min'] = date.today().replace(year=date.today().year - edad_max - 1)

        return cleaned_data



### CRUD ALBUM
class AlbumModelForm(forms.ModelForm):
    titulo = forms.CharField(
        
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    artista = forms.CharField(
        
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Album
        fields = ['titulo', 'artista', 'portada', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe aquí tu álbum',
                'rows': 4,
                'cols': 50
            }),
            'portada': forms.FileInput(attrs={
                'class': 'form-control'
                
            })
        }

    def clean(self):
        cleaned_data = super().clean()
        titulo = cleaned_data.get('titulo')
        artista = cleaned_data.get('artista')

    
        if not titulo:
            self.add_error('titulo', 'El título es obligatorio')
        elif len(titulo) > 200:
            self.add_error('titulo', 'El título no puede exceder los 200 caracteres')

        if not artista:
            self.add_error('artista', 'El artista es obligatorio')
        elif len(artista) > 200:
            self.add_error('artista', 'El nombre del artista no puede exceder los 200 caracteres')


        if titulo and artista:
            album_id = self.instance.id
            if Album.objects.filter(titulo=titulo, artista=artista).exclude(id=album_id).exists():
                self.add_error('titulo', 'Ya existe un álbum con este título y artista')

        return self.cleaned_data


class DetalleAlbumModelForm(forms.ModelForm):
    class Meta:
        model = DetalleAlbum
        fields = ['productor', 'estudio_grabacion', 'sello_discografico']
        widgets = {
            'productor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del productor'
            }),
            'estudio_grabacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Estudio de grabación'
            }),
            'sello_discografico': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sello discográfico'
            })
        }

    def clean(self):
        super().clean()
        productor = self.cleaned_data.get('productor')
        estudio = self.cleaned_data.get('estudio_grabacion')
        sello = self.cleaned_data.get('sello_discografico')

        if not productor:
            self.add_error('productor', 'El productor es obligatorio')
        elif len(productor) > 200:
            self.add_error('productor', 'El nombre del productor no puede exceder los 200 caracteres')

        if estudio and len(estudio) > 200:
            self.add_error('estudio_grabacion', 'El nombre del estudio no puede exceder los 200 caracteres')

        if sello and len(sello) > 100:
            self.add_error('sello_discografico', 'El nombre del sello no puede exceder los 100 caracteres')

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            for field in self.fields:
                if hasattr(self.instance, field):
                    self.fields[field].initial = getattr(self.instance, field)


class BusquedaAvanzadaAlbumForm(forms.Form):
    titulo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título'
        })
    )
    artista = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por artista'
        })
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        super().clean()

        if not any(self.cleaned_data.values()):
            self.add_error(None, 'Debes especificar al menos un criterio de búsqueda')

        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_desde', 'La fecha inicial no puede ser posterior a la fecha final')
            self.add_error('fecha_hasta', 'La fecha final no puede ser anterior a la fecha inicial')
        
        titulo = self.cleaned_data.get('titulo')
        if titulo and len(titulo) < 3:
            self.add_error('titulo', 'El título debe tener al menos 3 caracteres de búsqueda')

        artista = self.cleaned_data.get('artista')
        if artista and len(artista) < 3:
            self.add_error('artista', 'Ingresa al menos 3 caracteres para buscar por artista')

        return self.cleaned_data



class CancionForm(ModelForm):
    class Meta:
        model = Cancion
        fields = ['titulo', 'artista', 'portada', 'etiqueta', 'archivo_audio']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'artista': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'archivo_audio': forms.FileInput(attrs={'class': 'form-control'}),
            'portada': forms.FileInput(attrs={'class': 'form-control'}),
            'etiqueta': forms.Select(attrs={'class': 'form-control', 'required': True})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['archivo_audio'].required = False

    def clean(self):
        super().clean()
        titulo = self.cleaned_data.get('titulo')
        archivo = self.cleaned_data.get('archivo_audio')

        if not titulo:
            self.add_error('titulo', 'El título es obligatorio')
        elif len(titulo) < 3:
            self.add_error('titulo', 'El título debe tener al menos 3 caracteres')
        elif len(titulo) > 200:
            self.add_error('titulo', 'El título no puede exceder los 200 caracteres')

        if archivo:
            if not archivo.name.endswith(('.wav', '.mp3')):
                self.add_error('archivo_audio', 'Solo se permiten archivos .wav o .mp3')
            elif archivo.size > 70 * 1024 * 1024:  
                self.add_error('archivo_audio', 'El archivo no puede ser mayor a 70MB')
        elif not self.instance.pk:
            self.add_error('archivo_audio', 'El archivo de audio es obligatorio')

        return self.cleaned_data

class DetallesCancionForm(ModelForm):
    class Meta:
        model = DetallesCancion
        fields = ['letra', 'creditos', 'idioma']
        widgets = {
            'letra': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'creditos': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'idioma': forms.TextInput(attrs={'class': 'form-control'})
        }

    def clean(self):
        super().clean()

      
        creditos = self.cleaned_data.get('creditos')
        if creditos and len(creditos) > 1000:
            self.add_error('creditos', 'Los créditos no pueden exceder los 1000 caracteres')

        return self.cleaned_data


class BusquedaAvanzadaCancionForm(forms.Form):
    titulo = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título'
        })
    )
    
    artista = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por artista'
        })
    )
    
    etiqueta = forms.ChoiceField(
        choices=[('', 'Todas las categorías')] + Cancion.CATEGORIAS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    album = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por álbum'
        })
    )

    def clean(self):
        super().clean()

        if not any(self.cleaned_data.values()):
            self.add_error(None, 'Debes especificar al menos un criterio de búsqueda')

        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_desde', 'La fecha inicial no puede ser posterior a la fecha final')
            self.add_error('fecha_hasta', 'La fecha final no puede ser anterior a la fecha inicial')

        for field in ['titulo', 'artista', 'album']:
            value = self.cleaned_data.get(field)
            if value and len(value) < 3:
                self.add_error(field, f'Ingresa al menos 3 caracteres para buscar por {field}')

        return self.cleaned_data




class ComentarioModelForm(ModelForm):
    contenido = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Escribe tu comentario aquí...',
            'rows': 3,
            'cols': 50
        })
    )

    class Meta:
        model = Comentario
        fields = ['contenido']

    def clean(self):
        super().clean()
        contenido = self.cleaned_data.get('contenido')

        if not contenido:
            self.add_error('contenido', 'El contenido es obligatorio')
        elif len(contenido.strip()) < 1:
            self.add_error('contenido', 'El comentario no puede estar vacío')
        elif len(contenido) > 1000:
            self.add_error('contenido', 'El comentario no puede tener más de 1000 caracteres')
        elif contenido.strip().isspace():
            self.add_error('contenido', 'El comentario no puede tener solo espacios')
        
        return self.cleaned_data


class BusquedaAvanzadaComentarioForm(forms.Form):
    contenido = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar contenido...'
        })
    )

    usuario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre...'
        })
    )

    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        super().clean()

        if not any(self.cleaned_data.values()):
            self.add_error(None, "Debes especificar al menos un criterio de búsqueda")
        
        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error(None, "La fecha inicial no puede ser posterior a la fecha final")

        contenido = self.cleaned_data.get('contenido')
        if contenido and len(contenido) < 3:
            self.add_error('contenido', "El texto de búsqueda debe tener al menos tres caracteres")

        return self.cleaned_data


# MIRAR!!!!!
class PlaylistForm(ModelForm):
    canciones = forms.ModelMultipleChoiceField(
        queryset=Cancion.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input me-1'
        }),
        help_text="Selecciona las canciones que deseas agregar a la playlist"
    )

    class Meta:
        model = Playlist
        fields = ['nombre', 'descripcion', 'publica', 'canciones']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la playlist'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción de la playlist'
            }),
            'publica': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['canciones'].initial = self.instance.canciones.all()

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        descripcion = cleaned_data.get('descripcion')
        
        if nombre and len(nombre) < 3:
            self.add_error('nombre', 'El nombre de la playlist debe tener al menos 3 caracteres.')
        
        if descripcion and len(descripcion) > 500:
            self.add_error('descripcion', 'La descripción no puede tener más de 500 caracteres.')

        return cleaned_data

class BusquedaAvanzadaPlaylistForm(forms.Form):
    nombre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de playlist'
        })
    )
    
    usuario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nombre de usuario'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    publica = forms.ChoiceField(
        choices=[('', 'Todas'), ('True', 'Públicas'), ('False', 'Privadas')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        
   
        if not any(cleaned_data.values()):
            self.add_error(None, 'Debes especificar al menos un criterio de búsqueda')
        

        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            self.add_error('fecha_desde', 'La fecha inicial no puede ser posterior a la fecha final')
            self.add_error('fecha_hasta', 'La fecha final no puede ser anterior a la fecha inicial')
        
     
        for field in ['nombre', 'usuario']:
            value = cleaned_data.get(field)
            if value and len(value) < 3:
                self.add_error(field, f'Ingresa al menos 3 caracteres para buscar por {field}')

        return cleaned_data

    

class MensajePrivadoForm(ModelForm):
    class Meta:
        model = MensajePrivado
        fields = ['contenido']
        widgets = {
            'contenido': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Escribe tu mensaje aquí...',
                'rows': 3,
                'cols': 50
            })
        }

    def clean(self):
        super().clean()
        contenido = self.cleaned_data.get('contenido')
        
        if not contenido or contenido.isspace():
            self.add_error('contenido', "El mensaje no puede estar vacío o contener solo espacios")
        elif len(contenido.strip()) < 1:
            self.add_error('contenido', "El mensaje debe contener al menos 1 carácter")
        elif len(contenido) > 1000:
            self.add_error('contenido', "El mensaje no puede exceder los 1000 caracteres")

        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)



class BusquedaMensajesForm(forms.Form):
    contenido = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar en mensajes...'
        })
    )
    
    usuario = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario...'
        })
    )
    
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    def clean(self):
        super().clean()
        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')

        if fecha_desde and fecha_hasta and fecha_hasta < fecha_desde:
            self.add_error(None, "La fecha final no puede ser anterior a la fecha inicial")

        hoy = timezone.now().date()
        if fecha_hasta and fecha_hasta > hoy:
            self.add_error('fecha_hasta', "La fecha final no puede ser futura")
        if fecha_desde and fecha_desde > hoy:
            self.add_error('fecha_desde', "La fecha inicial no puede ser futura")

        return self.cleaned_data