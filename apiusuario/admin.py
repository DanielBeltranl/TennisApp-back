from django.contrib import admin
from django import forms
from django.contrib.auth.hashers import make_password
from .models import Usuario

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Información Personal', {
            'fields': ('nombre', 'apellidoPaterno', 'apellidoMaterno', 'sexo', 'edad')
        }),
        ('Credenciales y Contacto', {
            'fields': ('correo', 'contraseña')
        }),
        ('Datos Físicos y Perfil', {
            'fields': ('altura', 'peso', 'nivelUsuario')
        }),
    )

    list_display = ('correo', 'nombre', 'nivelUsuario')
    search_fields = ('correo', 'nombre')

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'contraseña':
            kwargs['widget'] = forms.PasswordInput(render_value=False)
        return super().formfield_for_dbfield(db_field, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if 'contraseña' in form.changed_data:
            # Encriptar si cambió la contraseña
            obj.contraseña = make_password(obj.contraseña)
        super().save_model(request, obj, form, change)