
from flask import Flask, render_template, redirect, request, jsonify, send_file
from main import *
from gostsig import *
import shifr
import sys
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


@app.route('/cipher_file', methods=['POST'])
def get_cipher_file():
    uploaded_file = request.files.get('file')
    key = request.form.get('key')
    if not uploaded_file:
        return jsonify({'error': 'Файл не получен'}), 400
    file_path = f"uploads/{uploaded_file.filename}"
    uploaded_file.save(file_path)
    
    encrypted_file_path = shifr.chifr_file(file_path, key)
    try:
        return send_file(encrypted_file_path, as_attachment=True, download_name=encrypted_file_path[7:])  # Скачивание с именем
    except Exception as e:
        return jsonify({'error': f'Ошибка при отправке файла: {str(e)}'}), 500
    


@app.route('/decipher_file', methods=['POST'])
def get_uncipher_file():
    uploaded_file = request.files.get('file')
    key = request.form.get('key')
    if not uploaded_file:
        return jsonify({'error': 'Файл не получен'}), 400
    file_path = f"uploads/{uploaded_file.filename}"
    uploaded_file.save(file_path)
    
    decrypted_file_path = shifr.unchifr_file(file_path, key)
    try:
        return send_file(decrypted_file_path, as_attachment=True, download_name='crypted_file')  # Скачивание с именем
    except Exception as e:
        return jsonify({'error': f'Ошибка при отправке файла: {str(e)}'}), 500


#6497B98333D63AFBEBC8F4228420065D4540008A7D9A139A6B81EA85CDF89F30

@app.route('/home/gen_key', methods=['GET'])
def key_gen():
    key = generate_key()

    return jsonify({"key": key})


@app.route('/sig', methods=['POST'])
def get_sig():
    uploaded_file = request.files.get('file')
    if not uploaded_file:
        return jsonify({'error': 'Файл не получен'}), 400
    file_path = f"uploads/{uploaded_file.filename}"
    uploaded_file.save(file_path)
    sig_path = gost(file_path)
    try:
        return send_file(sig_path, as_attachment=True, download_name='crypted_file')  # Скачивание с именем
    except Exception as e:
        return jsonify({'error': f'Ошибка при отправке файла: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


