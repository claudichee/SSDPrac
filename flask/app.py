from flask import Flask, render_template, request, redirect, url_for, session
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necessary for session management

def validate_password(password):
    # OWASP Top 10 Proactive Controls C6: Password Requirements
    # Minimum 8 characters in length
    if len(password) < 8:
        return False
    # At least one uppercase letter
    if not re.search(r'[A-Z]', password):
        return False
    # At least one lowercase letter
    if not re.search(r'[a-z]', password):
        return False
    # At least one digit
    if not re.search(r'\d', password):
        return False
    # At least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        password = request.form['password']
        if validate_password(password):
            session['password'] = password
            return redirect(url_for('welcome'))
        else:
            return render_template('home.html', error='Password does not meet requirements.')
    return render_template('home.html')

@app.route('/welcome')
def welcome():
    if 'password' in session:
        password = session['password']
        return render_template('welcome.html', password=password)
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('password', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
