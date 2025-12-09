
from flask import Flask, render_template, redirect, request, jsonify
from main import *

app = Flask(__name__, template_folder="static")

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



# добавила маршрут для хэшироания 
@app.route('/get_file_hash', methods=['POST'])
def get_file_hash():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'error': 'Файл не получен'}), 400
    
    if check_data_in_redis(uploaded_file.filename) is True:
        hash_value = get_data_from_redis(f'{uploaded_file.filename}:hash')
    else:

        file_path = f"uploads/{uploaded_file.filename}"
        uploaded_file.save(file_path)

        hash_value = get_hash_for_file(file_path)
    

    return jsonify({"hash": hash_value})



@app.route('/gen_key', methods=['POST'])
def key_gen():
    key = generate_key()
    return render_template({'key': key})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


