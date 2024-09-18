from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from app import db
from app.models import User, Todo
from app.forms import RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash

def configure_routes(app):
    # Hauptseite (Startseite)
    @app.route('/')
    def index():
        return render_template('index.html')

    # Registrierung
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            # Verwende 'pbkdf2:sha256' anstelle von 'sha256'
            hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
            new_user = User(username=form.username.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Erfolgreich registriert! Bitte melde dich an.')
            return redirect(url_for('login'))
        return render_template('register.html', form=form)

    # Login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('todo'))
            else:
                flash('Ungültiger Benutzername oder Passwort.')
        return render_template('login.html', form=form)

    # To-Do-Liste
    @app.route('/todo', methods=['GET', 'POST'])
    @login_required
    def todo():
        if request.method == 'POST':
            title = request.form['title']
            new_todo = Todo(title=title, user_id=current_user.id)
            db.session.add(new_todo)
            db.session.commit()

        todos = Todo.query.filter_by(user_id=current_user.id).all()
        return render_template('todo.html', todos=todos)

    # To-Do erledigt markieren
    @app.route('/todo/done/<int:todo_id>')
    @login_required
    def mark_done(todo_id):
        todo = Todo.query.get(todo_id)
        if todo and todo.user_id == current_user.id:
            todo.done = True
            db.session.commit()
        return redirect(url_for('todo'))

    # To-Do löschen
    @app.route('/todo/delete/<int:todo_id>')
    @login_required
    def delete(todo_id):
        todo = Todo.query.get(todo_id)
        if todo and todo.user_id == current_user.id:
            db.session.delete(todo)
            db.session.commit()
        return redirect(url_for('todo'))

    # API-Endpunkt: Alle To-Dos abrufen
    @app.route('/api/todos', methods=['GET'])
    @login_required
    def api_get_todos():
        todos = Todo.query.filter_by(user_id=current_user.id).all()
        return jsonify([{'id': todo.id, 'title': todo.title, 'done': todo.done} for todo in todos])

    # API-Endpunkt: Ein neues To-Do hinzufügen
    @app.route('/api/todos', methods=['POST'])
    @login_required
    def api_create_todo():
        data = request.get_json()
        if 'title' not in data:
            return jsonify({'error': 'Titel erforderlich'}), 400
        new_todo = Todo(title=data['title'], user_id=current_user.id)
        db.session.add(new_todo)
        db.session.commit()
        return jsonify({'id': new_todo.id, 'title': new_todo.title, 'done': new_todo.done}), 201

    # API-Endpunkt: Ein To-Do aktualisieren
    @app.route('/api/todos/<int:todo_id>', methods=['PUT'])
    @login_required
    def api_update_todo(todo_id):
        todo = Todo.query.get(todo_id)
        if not todo or todo.user_id != current_user.id:
            return jsonify({'error': 'To-Do nicht gefunden oder nicht autorisiert'}), 404

        data = request.get_json()
        todo.title = data.get('title', todo.title)
        todo.done = data.get('done', todo.done)
        db.session.commit()
        return jsonify({'id': todo.id, 'title': todo.title, 'done': todo.done})

    # API-Endpunkt: Ein To-Do löschen
    @app.route('/api/todos/<int:todo_id>', methods=['DELETE'])
    @login_required
    def api_delete_todo(todo_id):
        todo = Todo.query.get(todo_id)
        if not todo or todo.user_id != current_user.id:
            return jsonify({'error': 'To-Do nicht gefunden oder nicht autorisiert'}), 404

        db.session.delete(todo)
        db.session.commit()
        return jsonify({'message': 'To-Do erfolgreich gelöscht'}), 200

    # Abmelden
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))
