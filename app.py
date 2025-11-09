
from flask import Flask, render_template, redirect, request, jsonify
app = Flask(__name__, template_folder="static")
from main import *
@app.route('/')
def home_page():
    return render_template('auth.html')






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['id']
        password = request.form['password']
        print(user_id, password)
        print(authenticate_user(user_id, user_id))
        if authenticate_user(user_id, password):
            return redirect('home')
        else:
            return render_template('auth.html', login_message='Неверные данные')
    return render_template('auth.html')





@app.route('/home')
def reg_page():
    return render_template('index.html', value='shifr')


if __name__ == '__main__':
    app.run(debug=True)
