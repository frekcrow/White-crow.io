CROW, [04/09/2025 2:49 AM]
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import random
import string
import os

app = Flask(__name__)
CORS(app)

def init_db():
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS activation_codes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  code TEXT UNIQUE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  duration_days INTEGER,
                  is_used BOOLEAN DEFAULT FALSE,
                  used_at TIMESTAMP NULL,
                  device_id TEXT NULL,
                  expires_at TIMESTAMP NULL,
                  customer_name TEXT NULL,
                  customer_email TEXT NULL)''')
    conn.commit()
    conn.close()

def generate_activation_code(duration_days, customer_name="", customer_email="", prefix="ACT"):
    chars = string.ascii_uppercase + string.digits
    code = prefix + '-' + ''.join(random.choices(chars, k=12))
    
    created_at = datetime.datetime.now()
    expires_at = created_at + datetime.timedelta(days=duration_days)
    
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    c.execute("INSERT INTO activation_codes (code, duration_days, expires_at, customer_name, customer_email) VALUES (?, ?, ?, ?, ?)",
              (code, duration_days, expires_at, customer_name, customer_email))
    conn.commit()
    conn.close()
    
    return code

@app.route('/verify', methods=['POST'])
def verify_code():
    data = request.get_json()
    
    if not data or 'code' not in data or 'device_id' not in data:
        return jsonify({'valid': False, 'message': 'بيانات ناقصة'})
    
    code = data['code']
    device_id = data['device_id']
    
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM activation_codes WHERE code = ?", (code,))
    code_data = c.fetchone()
    
    if not code_data:
        conn.close()
        return jsonify({'valid': False, 'message': 'كود التفعيل غير صحيح'})
    
    code_id, db_code, created_at, duration_days, is_used, used_at, db_device_id, expires_at, customer_name, customer_email = code_data
    
    if is_used:
        if db_device_id == device_id:
            if datetime.datetime.now() < datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S"):
                remaining_days = (datetime.datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S") - datetime.datetime.now()).days
                conn.close()
                return jsonify({'valid': True, 'message': f'الكود مفعل. المدة المتبقية: {remaining_days} يوم'})
            else:
                conn.close()
                return jsonify({'valid': False, 'message': 'انتهت مدة اشتراكك'})
        else:
            conn.close()
            return jsonify({'valid': False, 'message': 'الكود مستخدم على جهاز آخر'})
    
    c.execute("UPDATE activation_codes SET is_used = TRUE, used_at = ?, device_id = ? WHERE code = ?",
              (datetime.datetime.now(), device_id, code))
    conn.commit()
    conn.close()
    
    return jsonify({'valid': True, 'message': f'تم التفعيل بنجاح. مدة الاشتراك: {duration_days} يوم'})

@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    
    if not data or 'duration_days' not in data:
        return jsonify({'success': False, 'error': 'مدة الاشتراك مطلوبة'})
    
    duration_days = data['duration_days']
    customer_name = data.get('customer_name', '')
    customer_email = data.get('customer_email', '')
    prefix = data.get('prefix', 'ACT')
    
    code = generate_activation_code(duration_days, customer_name, customer_email, prefix)
    
    return jsonify({'success': True, 'code': code, 'duration_days': duration_days})

@app.route('/codes', methods=['GET'])
def get_all_codes():
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM activation_codes ORDER BY created_at DESC")
    codes = c.fetchall()
    
    conn.close()
    
    codes_list = []

CROW, [04/09/2025 2:49 AM]
for code in codes:
        codes_list.append({
            'id': code[0],
            'code': code[1],
            'created_at': code[2],
            'duration_days': code[3],
            'is_used': bool(code[4]),
            'used_at': code[5],
            'device_id': code[6],
            'expires_at': code[7],
            'customer_name': code[8],
            'customer_email': code[9]
        })
    
    return jsonify(codes_list)

@app.route('/delete/<code_id>', methods=['DELETE'])
def delete_code(code_id):
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    
    c.execute("DELETE FROM activation_codes WHERE id = ?", (code_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

if name == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
