import re
from django.http import request
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib import messages
from .models import  Direccion, User, Producto, Bodega, Rol
import bcrypt

#Creacion de la pagina index para el loggeo.
def index(request):
    context = {
        'allroles' : Rol.objects.all().exclude(roles ='Admin')
    }

    return render(request, "login.html", context)

#Creacion de nuevos usuarios.
def create_user(request):
    if request.method == "POST":
        # Validation check before safe in our DB
        errors = User.objects.registration_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/')
        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            user_rol = Rol.objects.get(id = request.POST['user_rol']),
            email = request.POST['email'],
            password = hash_pw
        )
        
        request.session['logged_user'] = new_user.id

        return redirect('/user/dashboard')
    return redirect('/')

def login(request):
    if request.method == "POST":
        user = User.objects.filter(email = request.POST['email'])

        if user:
            log_user = user [0]

            if bcrypt.checkpw(request.POST['password'].encode(), log_user.password.encode()):
                request.session['logged_user'] = log_user.id
                return redirect('/user/dashboard')
        messages.error(request, "Email o password estan incorrectos volver a intentarlo")

    return redirect('/')

def logout(request):
    request.session.flush()
    return redirect('/')


def user_rol(request):

    context = {
        'allroles' : Rol.objects.all()
    }

    return render(request, "login.html", context)

def dashboard_rol(request): 
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')
    user_log = User.objects.get(id=request.session['logged_user'])
    context = {
        'logged_user' : User.objects.get(id=request.session['logged_user']),
        'google_api_key': settings.GOOGLE_API_KEY,
        'user_log': user_log,   
        'all_bod' : Bodega.objects.all(),  
        'all_dir' : Direccion.objects.all(),  
        'allroles': Rol.objects.all(),
        'all_users' : User.objects.all(),   
        'all_prod' : Producto.objects.all(),
        'user_dir' : Direccion.objects.filter(user_log_id =request.session['logged_user'] ),
        'user': User.objects.filter(id=request.session['logged_user']),
    }
    if user_log.user_rol.id == 2:
        return render(request, 'dashboard_ad.html', context)
    if user_log.user_rol.id == 1:
        return render(request, 'dashboard_cl.html', context)


#CRUD GESTION DIRECCIONES
def user_dir(request, number):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    context = {
        'user_dir' : Direccion.objects.get(user_dir_id = number)
    }

    return render(request, "direccion.html", context)

def createAddress(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    if request.method=='POST':
        errors = Direccion.objects.direccion_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/user/gest_direccion')
        
        add=Direccion.objects.create(
            nombre_dir = request.POST['nomdirec'],
            celular = request.POST['celular'],
            desc=request.POST['desc'],
            lat=request.POST['id_lat'],
            long=request.POST['id_lng'],
            user_log=User.objects.get(id=request.session['logged_user'])
        )
    return redirect('/user/gest_direccion')

def edit_dir(request, number):
    if request.method == "POST":
        errors = Direccion.objects.direccion_validator(request.POST)
        if len(errors) > 0:
            edit_dir = Direccion.objects.get(id=number)
            context = {
                    'edit_dir' : edit_dir
            }
            for key, value in errors.items():
                messages.error(request,value)
            return render(request, 'edit_dir.html',context)
        else:
            update_dir = Direccion.objects.get(id=request.POST['direccion_id'])
            update_dir.nombre_dir = request.POST['nomdirec']
            update_dir.user_log = User.objects.get(id=request.session['logged_user'])
            update_dir.lat = request.POST['id_lat']
            update_dir.long = request.POST['id_lng']
            update_dir.celular = request.POST['celular']
            update_dir.desc = request.POST['desc']
            update_dir.save()
            context = {
                'edit_dir' : update_dir,
                'google_api_key': settings.GOOGLE_API_KEY,
            }
            return redirect('/user/gest_direccion')
    edit_dir = Direccion.objects.get(id=number)
    context = {
        'edit_dir' : edit_dir
        }

    return render(request, 'edit_dir.html',context) 

def delete_dir(request, number):
    borr_direccion = Direccion.objects.get(id=number)
    borr_direccion.delete()
    return redirect('/user/gest_direccion')


def gest_direccion(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    user_log = User.objects.get(id=request.session['logged_user'])
    context = {
        'logged_user' : User.objects.get(id=request.session['logged_user']),
        'google_api_key': settings.GOOGLE_API_KEY,
        'user_log': user_log,
        'all_dir' : Direccion.objects.all(),
        'user_dir' : Direccion.objects.filter(user_log_id =request.session['logged_user'] )
    }
    if user_log.user_rol.id == 2:
        return render(request, 'creardir_adm.html', context)
    if user_log.user_rol.id == 1:
        return render(request, 'creardir_us.html', context)

def all_dir(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    context = {
        'all_dir' : Direccion.objects.all(),
        
    }

#CRUD GESTION DE USUARIOS ADMIN
def create_users(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')
    if request.method == "POST":
        # Validation check before safe in our DB
        errors = User.objects.registration_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/user/gestion_users')
        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            user_rol = Rol.objects.get(id = request.POST['user_rol']),
            email = request.POST['email'],
            password = hash_pw,
            )
    return redirect('/user/dashboard')

def all_users(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    context = {
        'all_users' : User.objects.all(),
        'allroles': Rol.objects.all(),
        'user': User.objects.get(id=request.session['logged_user']),
    }

    return render(request, "dashboard.html", context)

def read_user(request, number):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    context = {
        'user_ses' : User.objects.get(users_id=number)
    }

    return render(request, "mod_user.html", context)

def gest_users(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')
    user_log = User.objects.get(id=request.session['logged_user'])
    context = {
        'logged_user' : User.objects.get(id=request.session['logged_user']),
        'google_api_key': settings.GOOGLE_API_KEY,
        'all_users' : User.objects.all(),
        'user_log': user_log,
        'allroles': Rol.objects.all(),
        'user_ses' : User.objects.filter(user_rol_id =request.session['logged_user'])
    }
    if user_log.user_rol.id == 2:
        return render(request, 'crearuser.html', context)
    if user_log.user_rol.id == 1:
        return render(request, 'mod_user.html', context)

def edit_usr(request, number):
    if request.method=='GET':
        content={
            'user': User.objects.get(id=number),
            'allroles': Rol.objects.all()
        }
        
        return render(request,'edit_user.html', content)    

    if request.method == "POST":

        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        User.objects.filter(id=number).update(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            user_rol = Rol.objects.get(id= request.POST['user_rol']),
            email = request.POST['email'],
            password = hash_pw
)
        return redirect('/user/gestion_users')

def edit_usr_cl(request, number):
    if request.method=='GET':
        content={
            'user': User.objects.get(id=number),
            'allroles': Rol.objects.all()
        }
        
        return render(request,'edit_user_cl.html', content)    

    if request.method == "POST":
        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        User.objects.filter(id=number).update(
            first_name = request.POST['first_name'],
            last_name = request.POST['last_name'],
            user_rol = Rol.objects.get(id= request.POST['user_rol']),
            email = request.POST['email'],
            password = hash_pw
)
        return redirect('/user/gestion_users')
def delete_user(request, number):
    borr_user = User.objects.get(id=number)
    borr_user.delete()
    return redirect('/user/dashboard')

#CRUD GESTION DE BODEGA ADMIN
def create_bod(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')
    if request.method == "POST":
        errors = Bodega.objects.bod_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/user/gestion_bodega')
        new_bod = Bodega.objects.create(
            prod_bod = Producto.objects.get(id = request.POST['prod_bod']),
            guia_rem = request.POST['guia_rem'],
            fecha_ingr = request.POST['fecha_ingr'],
            cantidad_stock = request.POST['cantidad_stock'],
            precio_compra = request.POST['precio_compra'],
            precio_venta = request.POST['precio_venta'],
            )
    return redirect('/user/gestion_bodega')

def all_bod(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    context = {
        'all_bod' : Bodega.objects.all(),
        
    }

def gest_bod(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')
    context = {
        'logged_user' : User.objects.get(id=request.session['logged_user']),
        'google_api_key': settings.GOOGLE_API_KEY,
        'all_bod' : Bodega.objects.all(),
        'all_prod': Producto.objects.all(),
    }
    return render(request, 'crearbod.html', context)

def delete_bod(request, number):
    borr_bod = Bodega.objects.get(id=number)
    borr_bod.delete()
    return redirect('/user/gestion_bodega')

#CRUD GESTION DE PRODUCTO ADMIN
def create_prod(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')
    if request.method == "POST":
        errors = Producto.objects.prod_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/user/gestion_prod')
        new_prod = Producto.objects.create(
            nombre_prod = request.POST['nombre_prod'],
            peso = request.POST['peso'],
            tipo = request.POST['tipo'],
            color = request.POST['color'],
            )
    return redirect('/user/gestion_prod')

def all_prod(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')

    context = {
        'all_prod' : Producto.objects.all(),

    }

def gest_prod(request):
    if 'logged_user' not in request.session:
        messages.error(request, "Please register or please log in first")
        return redirect('/')
    context = {
        'logged_user' : User.objects.get(id=request.session['logged_user']),
        'all_prod' : Producto.objects.all(),
    }
    return render(request, 'crearprod.html', context)

def edit_prd(request, number):
    if request.method=='GET':
        content={
            'producto': Producto.objects.get(id=number),
            'all_prod': Producto.objects.all(),
            'all_bod' : Bodega.objects.all(),

        }
        
        return render(request,'edit_prod.html', content)    

    if request.method == "POST":
        errors = Producto.objects.prod_validator(request.POST)
        if len(errors) > 0:
            for key,value in errors.items():
                messages.error(request, value)
            return redirect('/user/gestion_prod')
        Producto.objects.filter(id=number).update(
            nombre_prod = request.POST['nombre_prod'],
            peso = request.POST['peso'],
            tipo = request.POST['tipo'],
            color = request.POST['color'],
)
        return redirect('/user/gestion_prod')

def delete_prod(request, number):
    borr_prod = Producto.objects.get(id=number)
    borr_prod.delete()
    return redirect('/user/gestion_prod')
