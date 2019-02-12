# -*- coding: utf-8 -*-
# quiz-orm/views.py

from flask import Flask
from flask import render_template, request, redirect, url_for, abort, flash
from modele import *
from forms import *

app = Flask(__name__)

@app.route('/')
def index():
    """Strona główna"""
    return render_template('index.html')

@app.route("/lista_klas")
def lista_klas():
    klasa = Klasa().select()
    if not klasa.count():
        pass
    return render_template('lista.html', pytania=pytania)

@app.route("/lista_uczniow", methods=['GET', 'POST'])
def lista_uczniow():
    
    print(request.form)
    
    if request.method == 'POST':
        wynik = 0
        for pid, oid in request.form.items():
            if Odpowiedz().get(Odpowiedz.id == int(oid)).odpok:
                wynik += 1
                
        flash('Poprawnych odpowiedzi: {}'.format(wynik), 'info')
        return redirect(url_for('hello'))
    
    pytania = Pytanie().select().join(Odpowiedz).distinct()
    return render_template('quiz.html', pytania=pytania)


def flash_errors(form):
    """Odczytanie wszystkich błędów formularza i przygotowanie komunikatów"""
    for field, errors in form.errors.items():
        for error in errors:
            if type(error) is list:
                error = error[0]
            flash("Błąd: {}. Pole: {}".format(
                error,
                getattr(form, field).label.text))


@app.route("/dodaj_klase", methods=['GET', 'POST'])
def dodaj():
    form = DodajForm()
    form.kategoria.choices = [(k.id, k.kategoria) for k in Klasa.select()]
    
    if form.validate_on_submit():
        p = Pytanie(pytanie=form.pytanie.data, kategoria=form.kategoria.data)
        p.save()
        for o in form.odpowiedzi.data:
            odp = Odpowiedz(odpowiedz=o['odpowiedz'],
                            pytanie=p.id,
                            odpok=int(o['odpok']))
            odp.save()
        flash("Dodano pytanie: {}".format(form.pytanie.data))
        return redirect(url_for('lista'))
    elif request.method == 'POST':
        flash_errors(form)
    
    return render_template('dodaj.html', form=form)

def get_or_404(pid):
    try:
        p = Pytanie.get_by_id(pid)
        return p
    except Pytanie.DoesNotExist:
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route("/usun/<int:pid>", methods=['GET', 'POST'])
def usun(pid):
    p = get_or_404(pid)
    if request.method == "POST":
        flash("Usunięto pytanie: {}".format(p.pytanie))
        for o in Odpowiedz.select().where(Odpowiedz.pytanie == p.id):
            o.delete_instance()
        p.delete_instance()
        return redirect(url_for('lista'))
    return render_template('usun.html', pytanie=p)

@app.route("/edytuj/<int:pid>", methods=['GET', 'POST'])
def edytuj(pid):
    p = get_or_404(pid)
    
    form = DodajForm(obj=p)
    form.kategoria.choices = [(k.id, k.kategoria) for k in Kategoria.select()]
    form.kategoria.data = p.kategoria.id
    
    if form.validate_on_submit():
        p.pytanie = form.pytanie.data
        p.kategoria = form.kategoria.data
        p.save()
        for o in form.odpowiedzi.data:
            odp = Odpowiedz.get_by_id(o['id'])
            odp.odpowiedz = o['odpowiedz']
            odp.odpok = int(o['odpok'])
            odp.save()
        flash("Zaktualizowano pytanie: {}".format(form.pytanie.data))
        return redirect(url_for('lista'))
    
    elif request.method == 'POST':
        flash_errors(form)
    
    odpowiedzi = []
    for o in Odpowiedz.select().where(Odpowiedz.pytanie == p.id).dicts():
        odpowiedz.append(o)
    form.odpowiedz(data=odpowiedzi)
        
    return render_template('edytuj.html', form=form)
