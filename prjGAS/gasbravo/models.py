from django.db import models
from django.db.models.base import Model
from django.db.models.fields import DateField, IntegerField
from datetime import date
import re
# Create your models here.

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.+_-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'[0-9]')
NUM_REGEX = re.compile(r'[a-zA-Z]')

class UserManager(models.Manager):
    def registration_validator(self, postData):
        # ALL THE VALIDATION FOR THE FORM
        errors = {}
        if len(postData['first_name']) < 1 :
            errors['first_name'] = "Nombre no valido debe tener al menos 2 caracteres."
        if len(postData['last_name']) < 1:
            errors['last_name'] = "Apellido no valido. debe tener al menos 2 caracteres"
        if NAME_REGEX.search(postData['first_name']):
            errors["fist_name"] = "First name cannot contain any numbers"
        if NAME_REGEX.search(postData['last_name']):
            errors["last_name"] = "Last name cannot contain any numbers"
        if not EMAIL_REGEX.match(postData['email']):   
            errors['email'] = "Invalid email address!"
        users_with_email = User.objects.filter(email = postData['email'])
        if len(users_with_email) >= 1:
            errors['duplicate'] = "Email already exists."
        if len(postData['password']) < 7:
            errors['password'] = "El Password debe tener al menos 8 caracteres"
        if postData['password'] != postData['confirm_password']:
            errors['pw_match'] = "Password must match!"
        return errors 

class DireccionManager(models.Manager):
    def direccion_validator(self,postData):
        errors = {}
        if len(postData['nomdirec']) < 2:
            errors['nomdirec'] = "El nombre de la direción debe tener mas de 3 caracteres"
        if len(postData['celular']) != 10:
            errors['celular'] = "El Numero de celular es de 10 digitos"
        if NUM_REGEX.search(postData['celular']):
            errors["last_name"] = "No se admiten letras en en celular"        
        if len(postData['desc']) < 5:
            errors['desc'] = "La descripción debe tener mas de 5 caracteres"
        return errors

class ProductoManager(models.Manager):
    def prod_validator(self,postData):
        errors = {}
        if len(postData['nombre_prod']) < 2:
            errors['nombre_prod'] = "El nombre del producto debe tener mas de 3 caracteres"
        if len(postData['peso']) < 1:
            errors['peso'] = "El peso del cilindro debe tener mas de 1 caracter"
        if len(postData['tipo']) < 4:
            errors['tipo'] = "El tipo del cilindro debe tener mas de 5 caracteres"
        if len(postData['color']) < 2:
            errors['color'] = "El color del cilindro debe tener mas de 3 caracteres"

        return errors
    
class BodegaManager(models.Manager):
    def bod_validator(self,postData):
        errors = {}
        current_date = date.today()
        if len(postData['cantidad_stock']) < 1:
            errors['cantidad_stock'] = "La cantidad de stock debe ser mayor que 0"
        if len(postData['guia_rem']) < 1:
            errors['guia_rem'] = "La guia de remición debe tener mas de 1 caracter"
        if len(postData['precio_compra']) == 0:
            errors['precio_compra'] = "El precio de compra no puede ser 0"
        if len(postData['precio_venta']) == 0:
            errors['precio_venta'] = "El precio de venta no puede ser 0"
        if postData['fecha_ingr'] > current_date.strftime("%Y-%m-%d"):
            errors['fecha_ingr'] = "La fecha de ingreso no puede estar en el futuro"
        return errors



class Rol (models.Model):
    ROLES = (
        ('Cliente', 'Cliente'),
        ('Admin', 'Admin'),
    )
    roles = models.CharField(max_length=50, choices = ROLES, null=True)

class User (models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=55)
    email = models.CharField(max_length=55)
    password = models.CharField(max_length=55)
    user_rol = models.ForeignKey(Rol, related_name="user_rol", on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = UserManager()

class Direccion (models.Model):
    nombre_dir = models.CharField(max_length=50)
    user_log = models.ForeignKey(User, related_name="user_log", on_delete=models.CASCADE)
    lat = models.CharField(max_length=50)
    long = models.CharField(max_length=50)
    celular =models.CharField(max_length=10)
    desc = models.TextField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = DireccionManager()

class Producto (models.Model):
    nombre_prod = models.CharField(max_length=30)
    peso = models.CharField(max_length=2)
    tipo = models.CharField(max_length=25)
    color = models.CharField(max_length=25, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = ProductoManager()

class Bodega (models.Model):
    prod_bod = models.ForeignKey(Producto, related_name="prod_bod", on_delete=models.CASCADE)
    guia_rem = models.CharField(max_length=30)
    fecha_ingr = models.DateField(null=True)
    cantidad_stock = models.IntegerField()
    precio_compra = models.DecimalField(max_digits=5, decimal_places=4, default=0.00, null=True)
    precio_venta = models.DecimalField(max_digits=5, decimal_places=4, default=0.00, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    objects = BodegaManager()

class Status_Ped (models.Model):
    status = models.CharField(max_length=30)    
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


class Pedido (models.Model):
    dire_id = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    stat_id = models.ForeignKey(Status_Ped, on_delete=models.CASCADE)
    usr_id = models.ForeignKey(User, on_delete=models.CASCADE)
    ped_prod = models.ManyToManyField(Producto, through='Pedido_prod')
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True) 

class Pedido_prod (models.Model):
    ped_id = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    prod_id = models.ForeignKey(Producto, on_delete=models.CASCADE)  
    cantidad = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)   










