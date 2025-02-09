from unicodedata import category
from flask import Blueprint, render_template, request, redirect, flash, jsonify, url_for, abort
from flask_login import login_required, current_user

#from models.tables import Estabelecimento 
from .models import Note
from .models import Items
from .models import Estabelecimentos


from . import db
import json

import os

"""
    Como o arquivo estará em binario será necessário essa lib para salvar
"""
from werkzeug.utils import secure_filename

UPLOAD = 'website/static/uploads'

UPLOAD_FOLDER = os.path.join(os.getcwd(), UPLOAD)

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
#@login_required
def home():
    
    if request.method == 'POST':
        note = request.form.get('note')

        if len(note) < 1:
            flash('Note está muito curto', category='error')
        else:
            new_note = Note(data = note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note adicionado', category='success')
    return render_template("home.html", user=current_user)

@views.route('/delete-note', methods=['POST'])
def delete_note():
    note = json.loads(request.data)
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()
    return jsonify({})

@views.route('/admin')
@login_required
def admin():
    return render_template("admin.html", user=current_user)

@views.route('/cadastro')
def teste():
    return render_template("cadastro.html", user=current_user)

@views.route('/form', methods=['GET','POST'])
def form():
    mercado = Estabelecimentos.query.all()
    if request.method == 'POST':
        estabelecimento_id = request.form.get('estabelecimento_id')
        tipo_item = request.form.get('tipo_item')
        nome_item = request.form.get('nome_item')
        marca = request.form.get('marca_item')
        volume_tipo =request.form.get('volume_tipo')
        volume = request.form.get('volume')
        qtd_maxima = request.form.get('qtd_maxima')
        valor = request.form.get('valor')
        
        file = request.files['foto']
        namefoto = file.filename
        
        
        savePath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(savePath)

        data_fim_promocao = request.form.get('data_fim_promocao')

        # Criar as validações dos inputs aqui

        new_item = Items( tipo_item=tipo_item, nome_item=nome_item, 
        marca_item=marca, volume_tipo = volume_tipo,
        volume= volume,  qtd_maxima=qtd_maxima, valor=valor,foto=namefoto,
        data_fim_promocao=data_fim_promocao, estabelecimento_id=estabelecimento_id
        )


        db.session.add(new_item)
        db.session.commit()
        flash('Produto salvo com sucesso', category='success')
        return redirect(url_for('views.form'))
    #else:
        #flash('Erro ao salvar o produto', category='error')
    return render_template('form.html', mercado=mercado, user=current_user)

#Googlemaps
class Comercio:
    def __init__(self, key, name, lat, lng):
        self.key  = key
        self.name = name
        self.lat  = lat
        self.lng  = lng

# AS coordenadas do endereço
comercios = (
    Comercio('mercadoA',      'Mercadinho A',  -23.571319422733524, -46.414629246163614),
    Comercio('mercadoB', 'Mercadinho B',           -23.591198056010676, -46.403604962487194),
    Comercio('mercadoC',     'Mercadinho C', -23.588869063417768, -46.40864850869)
)
comercios_by_key = {comercio.key: comercio for comercio in comercios}


@views.route('/mercadoa' ) #endpoints
def mercadoa ():
    mercado = db.session.query(Estabelecimentos).filter(Estabelecimentos.id==1)

    dados_items = db.session.query(Items).filter(Items.estabelecimento_id==1)
    return render_template("mercadoa.html", mercado=mercado , ofertas=dados_items, comercios=comercios, user=current_user)

@views.route ( '/mercadob' )
def  mercadob ():
    mercado = db.session.query(Estabelecimentos).filter(Estabelecimentos.id==2)

    dados_items = db.session.query(Items).filter(Items.estabelecimento_id==2)
    return  render_template ( "mercadob.html",comercios=comercios,  ofertas=dados_items,  user = current_user  )

@views.route( '/mercadoc' )
def  mercado ():
     mercado = db.session.query(Estabelecimentos).filter(Estabelecimentos.id==3)

     dados_items = db.session.query(Items).filter(Items.estabelecimento_id==3)

     return  render_template ( "mercadoc.html", comercios=comercios, ofertas=dados_items, user = current_user )

#GoogleMaps
@views.route("/<comercio_code>")
def show_comercio(comercio_code):
    comercio = comercios_by_key.get(comercio_code)
    if comercio:
        return render_template('map.html', comercio=comercio)
    else:
        abort(404)



