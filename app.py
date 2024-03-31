import os
from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import random

# Get the current directory of the script
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, static_url_path='/static')
app.secret_key = 'a1484361219002e4d76c49b230b01f88'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.db')
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    wins = db.Column(db.Integer, default=0)

@app.before_request
def before_request():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'username' in session:
        username = session['username']
        user = User.query.filter(User.username.ilike(username)).first()
        if user is None:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()
        wins = user.wins
        if request.method == 'POST':
            if 'logout' in request.form:
                session.pop('username', None)  # Clear the username from the session
                return redirect('/')
            user_choice = request.form['choice']
            computer_choice = random.choice(['rock', 'paper', 'scissors'])
            result = determine_winner(user_choice, computer_choice)
            if result == 'win':
                user.wins += 1
                db.session.commit()
            return render_template('index.html', username=username, wins=user.wins, result=result.capitalize(), user_choice=user_choice.capitalize(), computer_choice=computer_choice.capitalize())
        return render_template('index.html', username=username, wins=wins)
    else:
        if request.method == 'POST':
            username = request.form['username']
            session['username'] = username
            return redirect('/')
        return render_template('index.html')


def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return 'tie'
    elif (user_choice == 'rock' and computer_choice == 'scissors') or \
         (user_choice == 'paper' and computer_choice == 'rock') or \
         (user_choice == 'scissors' and computer_choice == 'paper'):
        return 'win'
    else:
        return 'lose'

if __name__ == '__main__':
    app.run(debug=True)