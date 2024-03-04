import sys

import sqlalchemy

from app import app, engine, login_manager
from flask_login import login_required, login_user, current_user, logout_user
from flask import render_template, redirect, flash, url_for
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import *
from app.forms import LoginForm
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from faker import Faker
from random import randint, choice


@login_manager.user_loader
def load_user(user_id):
    return Session(engine).query(Users).get(user_id)


def create_rows(rows: list):
    try:
        with Session(engine) as session, session.begin():
            for row in rows:
                session.add(row)
            session.commit()

    except IntegrityError as e:
        print(f"[ ERROR ] create rows error: {e}", file=sys.stderr)


def get_column_values(column):
    assert isinstance(column, sqlalchemy.orm.attributes.InstrumentedAttribute), \
        AssertionError(f'column must be sqlalchemy.orm.attributes.InstrumentedAttribute, not {type(column)}')

    with Session(engine) as session:
        return session.scalars(select(column).order_by(column)).all()


def admin_required(func):  # admin_required decorator
    def check(*args, **kwargs):
        print(current_user.role)
        if not current_user.role:
            flash('Недостаточно прав')
            return redirect(url_for("index"))
        return func(*args, **kwargs)

    check.__name__ = func.__name__
    return check


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Session(engine).query(Users).filter(Users.login == form.login.data).first()
        if user and user.check_password(pw=form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('index'))
        flash('Неверный логин или пароль', 'error')
        return redirect(url_for('login'))
    return render_template('login.html', form=form)


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    logout_user()
    flash("Вы вышли из системы")
    return redirect(url_for('login'))


@app.route("/requisites", methods=['GET'])
@login_required
def show_requisites():
    data = Session(engine).query(Requisites).join(Invoices)
    print(data)

    return render_template('requisites.html', data=data)


@app.route("/invoices", methods=['GET'])
@login_required
@admin_required
def show_invoices():
    data = Session(engine).query(Invoices).join(Requisites)
    return render_template('invoices.html', data=data)


@app.route("/users", methods=['GET'])
@login_required
@admin_required
def show_users():
    data = Session(engine).query(Users)
    return render_template('users.html', data=data)


@app.route("/create_fake_data")
def create_fake_data():
    fake = Faker('ru-RU')

    # Fake requisites
    length = len(get_column_values(Requisites.id))
    if length < 100:
        print(f'[ INFO ] Generating fake Requisites: '
              f'{length} rows already exist, '
              f'{100 - length} will be added.', file=sys.stdout)
        requisites = []
        for i in range(100 - length):
            requisite = Requisites(
                # id = ,
                payment_type=randint(0, 1),
                is_credit=choice([True, False, False]),
                fio=fake.name(),
                phone_number=fake.phone_number(),
                limit=choice([0, 0, 0, 0, 0, 0, 0, 0, 0, 10000, 25000, 100000])
            )
            requisites.append(requisite)
        create_rows(requisites)
        print(f'[ INFO ] {len(requisites)} rows created', file=sys.stdout)
    else:
        print(f'[ INFO ] already enough requisites - {length}', file=sys.stdout)

    # Fake invoices
    length = len(get_column_values(Invoices.id))
    if length < 5000:
        print(f'[ INFO ] Generating fake Invoices: {length} rows already exist, {100 - length} will be added.',
              file=sys.stdout)
        invoices = []
        for i in range(5000 - length):
            invoice = Invoices(
                sum=randint(1000, 100000),
                status=choice([1, 1, 1, 1, 1, 0, 2]),
                requisites_id=choice(get_column_values(Requisites.id))
            )
            invoices.append(invoice)
        print(f'[ INFO ] {len(invoices)} rows created', file=sys.stdout)
        create_rows(invoices)
    else:
        print(f'[ INFO ] already enough invoices - {length}', file=sys.stdout)

    roles = get_column_values(Users.role)
    users = []
    if True not in roles:
        users.append(Users(
            login="admin",
            role=True,
            password_hash=generate_password_hash('asdfg123')
        ))
    if False not in roles:
        users.append(Users(
            login="user1",
            role=False,
            password_hash=generate_password_hash('123')
        ))
    create_rows(users)
    for i in users:
        print(f'[ INFO ] {i} created', file=sys.stdout)

    return str('Finished'), 200
