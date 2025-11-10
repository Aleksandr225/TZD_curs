
from flask import Flask, render_template, redirect, request, jsonify
app = Flask(__name__, template_folder="static")
from main import *
@app.route('/')
def home_page():
    return render_template('auth.html')






@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        active_tab = request.form.get('active_tab', 'login')
        
        if active_tab == 'login':
            user_id = request.form['id']
            password = request.form['password']
        
            if check_if_user_exists(user_id, password) is True:
                return redirect('home')
            else:
                return render_template('auth.html', login_message='Неверные данные')
            
        else:
            user_id = request.form['id']
            password = request.form['password']
            name = request.form['name']
            if check_if_user_exists(user_id, password) is True:
                return render_template('auth.html', login_message='Такой пользователь уже существует')
            else:
                if register_user(user_id, name, password) is True:
                    return redirect('home')
                else:
                    return render_template('auth.html', login_message='Неверные данные')

    return render_template('auth.html')







@app.route('/home')
def reg_page():
    return render_template('index.html', value='shifr')


if __name__ == '__main__':
    app.run(debug=True)
