from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import random
import string
import os

app = Flask(__name__)
CORS(app)

# تهيئة قاعدة البيانات
def init_database():
    connection = sqlite3.connect('activation_system.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activation_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_days INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            device_id TEXT NULL,
            used_at TIMESTAMP NULL,
            customer_name TEXT NULL,
            customer_email TEXT NULL
        )
    ''')
    
    connection.commit()
    connection.close()

# توليد كود تفعيل فريد
def create_activation_code(days_duration, name="", email="", code_prefix="ACT"):
    characters = string.ascii_uppercase + string.digits
    random_code = code_prefix + '-' + ''.join(random.choices(characters, k=10))
    
    created_date = datetime.datetime.now()
    
    db_connection = sqlite3.connect('activation_system.db')
    db_cursor = db_connection.cursor()
    
    db_cursor.execute(
        "INSERT INTO activation_codes (code, duration_days, customer_name, customer_email) VALUES (?, ?, ?, ?)",
        (random_code, days_duration, name, email)
    )
    
    db_connection.commit()
    db_connection.close()
    
    return random_code

# التحقق من صحة كود التفعيل
@app.route('/validate', methods=['POST'])
def validate_activation_code():
    request_data = request.get_json()
    
    if not request_data or 'activation_code' not in request_data or 'device_id' not in request_data:
        return jsonify({'success': False, 'message': 'بيانات الطلب غير مكتملة'})
    
    input_code = request_data['activation_code']
    device_identifier = request_data['device_id']
    
    db_connection = sqlite3.connect('activation_system.db')
    db_cursor = db_connection.cursor()
    
    db_cursor.execute("SELECT * FROM activation_codes WHERE code = ?", (input_code,))
    code_record = db_cursor.fetchone()
    
    if not code_record:
        db_connection.close()
        return jsonify({'success': False, 'message': 'كود التفعيل غير صحيح'})
    
    record_id, code_value, created_date, days_duration, is_active, device_id, used_date, customer_name, customer_email = code_record
    
    if not is_active:
        db_connection.close()
        return jsonify({'success': False, 'message': 'كود التفعيل معطل'})
    
    if device_id:
        if device_id == device_identifier:
            db_connection.close()
            return jsonify({'success': True, 'message': 'تم تفعيل هذا الجهاز مسبقاً'})
        else:
            db_connection.close()
            return jsonify({'success': False, 'message': 'كود التفعيل مستخدم على جهاز آخر'})
    
    current_time = datetime.datetime.now()
    db_cursor.execute(
        "UPDATE activation_codes SET device_id = ?, used_at = ? WHERE code = ?",
        (device_identifier, current_time, input_code)
    )
    
    db_connection.commit()
    db_connection.close()
    
    return jsonify({'success': True, 'message': 'تم تفعيل التطبيق بنجاح', 'days': days_duration})

# إنشاء كود تفعيل جديد
@app.route('/create', methods=['POST'])
def generate_new_code():
    request_data = request.get_json()
    
    if not request_data or 'days_duration' not in request_data:
        return jsonify({'success': False, 'error': 'يجب تحديد مدة الاشتراك'})
    
    days_duration = request_data['days_duration']
    customer_name = request_data.get('customer_name', '')
    customer_email = request_data.get('customer_email', '')
    code_prefix = request_data.get('prefix', 'ACT')
    
    new_code = create_activation_code(days_duration, customer_name, customer_email, code_prefix)
    
    return jsonify({'success': True, 'activation_code': new_code, 'days_duration': days_duration})

# الحصول على جميع أكواد التفعيل
@app.route('/all-codes', methods=['GET'])
#
def get_all_codes():

db_connection = sqlite3.connect('activation_system.db')
#
    db_cursor = db_connection.cursor()
    
    db_cursor.execute("SELECT * FROM activation_codes ORDER BY created_at DESC")
    all_codes = db_cursor.fetchall()
    
    db_connection.close()
    
    codes_list = []
    for code in all_codes:
        codes_list.append({
            'id': code[0],
            'code': code[1],
            'created_at': code[2],
            'duration_days': code[3],
            'is_active': bool(code[4]),
            'device_id': code[5],
            'used_at': code[6],
            'customer_name': code[7],
            'customer_email': code[8]
        })
    
    return jsonify(codes_list)

# حذف كود تفعيل
@app.route('/remove/<int:code_id>', methods=['DELETE'])
def remove_code(code_id):
    db_connection = sqlite3.connect('activation_system.db')
    db_cursor = db_connection.cursor()
    
    db_cursor.execute("DELETE FROM activation_codes WHERE id = ?", (code_id,))
    db_connection.commit()
    db_connection.close()
    
    return jsonify({'success': True})

# نقطة دخول التطبيق
if name == '__main__':
    init_database()
    server_port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=server_port)
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import random
import string
import os

app = Flask(__name__)
CORS(app)

# تهيئة قاعدة البيانات
def init_database():
    connection = sqlite3.connect('activation_system.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activation_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duration_days INTEGER NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            device_id TEXT NULL,
            used_at TIMESTAMP NULL,
            customer_name TEXT NULL,
            customer_email TEXT NULL
        )
    ''')
    
    connection.commit()
    connection.close()

# توليد كود تفعيل فريد
def create_activation_code(days_duration, name="", email="", code_prefix="ACT"):
    characters = string.ascii_uppercase + string.digits
    random_code = code_prefix + '-' + ''.join(random.choices(characters, k=10))
    
    created_date = datetime.datetime.now()
    
    db_connection = sqlite3.connect('activation_system.db')
    db_cursor = db_connection.cursor()
    
    db_cursor.execute(
        "INSERT INTO activation_codes (code, duration_days, customer_name, customer_email) VALUES (?, ?, ?, ?)",
        (random_code, days_duration, name, email)
    )
    
    db_connection.commit()
    db_connection.close()
    
    return random_code

# التحقق من صحة كود التفعيل
@app.route('/validate', methods=['POST'])
def validate_activation_code():
    request_data = request.get_json()
    
    if not request_data or 'activation_code' not in request_data or 'device_id' not in request_data:
        return jsonify({'success': False, 'message': 'بيانات الطلب غير مكتملة'})
    
    input_code = request_data['activation_code']
    device_identifier = request_data['device_id']
    
    db_connection = sqlite3.connect('activation_system.db')
    db_cursor = db_connection.cursor()
    
    db_cursor.execute("SELECT * FROM activation_codes WHERE code = ?", (input_code,))
    code_record = db_cursor.fetchone()
    
    if not code_record:
        db_connection.close()
        return jsonify({'success': False, 'message': 'كود التفعيل غير صحيح'})
    
    record_id, code_value, created_date, days_duration, is_active, device_id, used_date, customer_name, customer_email = code_record
    
    if not is_active:
        db_connection.close()
        return jsonify({'success': False, 'message': 'كود التفعيل معطل'})
    
    if device_id:
        if device_id == device_identifier:
            db_connection.close()
            return jsonify({'success': True, 'message': 'تم تفعيل هذا الجهاز مسبقاً'})
        else:
            db_connection.close()
            return jsonify({'success': False, 'message': 'كود التفعيل مستخدم على جهاز آخر'})
    
    current_time = datetime.datetime.now()
    db_cursor.execute(
        "UPDATE activation_codes SET device_id = ?, used_at = ? WHERE code = ?",
        (device_identifier, current_time, input_code)
    )
    
    db_connection.commit()
    db_connection.close()
    
    return jsonify({'success': True, 'message': 'تم تفعيل التطبيق بنجاح', 'days': days_duration})

# إنشاء كود تفعيل جديد
@app.route('/create', methods=['POST'])
def generate_new_code():
    request_data = request.get_json()
    
    if not request_data or 'days_duration' not in request_data:
        return jsonify({'success': False, 'error': 'يجب تحديد مدة الاشتراك'})
    
    days_duration = request_data['days_duration']
    customer_name = request_data.get('customer_name', '')
    customer_email = request_data.get('customer_email', '')
    code_prefix = request_data.get('prefix', 'ACT')
    
    new_code = create_activation_code(days_duration, customer_name, customer_email, code_prefix)
    
    return jsonify({'success': True, 'activation_code': new_code, 'days_duration': days_duration})

# الحصول على جميع أكواد التفعيل
@app.route('/all-codes', methods=['GET'])
def get_all_codes():

db_connection = sqlite3.connect('activation_system.db')
    db_cursor = db_connection.cursor()
    
    db_cursor.execute("SELECT * FROM activation_codes ORDER BY created_at DESC")
    all_codes = db_cursor.fetchall()
    
    db_connection.close()
    
    codes_list = []
    for code in all_codes:
        codes_list.append({
            'id': code[0],
            'code': code[1],
            'created_at': code[2],
            'duration_days': code[3],
            'is_active': bool(code[4]),
            'device_id': code[5],
            'used_at': code[6],
            'customer_name': code[7],
            'customer_email': code[8]
        })
    
    return jsonify(codes_list)

# حذف كود تفعيل
@app.route('/remove/<int:code_id>', methods=['DELETE'])
def remove_code(code_id):
    db_connection = sqlite3.connect('activation_system.db')
    db_cursor = db_connection.cursor()
    
    db_cursor.execute("DELETE FROM activation_codes WHERE id = ?", (code_id,))
    db_connection.commit()
    db_connection.close()
    
    return jsonify({'success': True})

# نقطة دخول التطبيق
if name == '__main__':
    init_database()
    server_port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=server_port)






