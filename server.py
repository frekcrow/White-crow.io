from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import datetime
import random
import string
import os

app = Flask(__name__)
CORS(app)

# تكوين قاعدة البيانات
def init_db():
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS codes
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  code TEXT UNIQUE,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  duration_days INTEGER,
                  is_active BOOLEAN DEFAULT TRUE,
                  device_id TEXT,
                  used_at TIMESTAMP)''')
    conn.commit()
    conn.close()

# توليد كود فريد
def generate_code(length=12):
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route('/activate', methods=['POST'])
def activate():
    data = request.get_json()
    if not data or 'code' not in data or 'device_id' not in data:
        return jsonify({'valid': False, 'message': 'بيانات غير مكتملة'})
    
    code = data['code'].strip().upper()
    device_id = data['device_id']
    
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    
    c.execute("SELECT * FROM codes WHERE code = ?", (code,))
    result = c.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'valid': False, 'message': 'كود التفعيل غير صحيح'})
    
    code_id, db_code, created_at, duration_days, is_active, db_device_id, used_at = result
    
    if not is_active:
        conn.close()
        return jsonify({'valid': False, 'message': 'هذا الكود معطل'})
    
    if db_device_id:
        if db_device_id == device_id:
            conn.close()
            return jsonify({'valid': True, 'message': 'التطبيق مفعل مسبقاً'})
        else:
            conn.close()
            return jsonify({'valid': False, 'message': 'الكود مستخدم على جهاز آخر'})
    
    # تفعيل الكود
    c.execute("UPDATE codes SET device_id = ?, used_at = ? WHERE code = ?",
              (device_id, datetime.datetime.now(), code))
    conn.commit()
    conn.close()
    
    return jsonify({'valid': True, 'message': 'تم التفعيل بنجاح'})

@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    if not data or 'duration_days' not in data:
        return jsonify({'error': 'مدة الاشتراك مطلوبة'}), 400
    
    duration_days = data['duration_days']
    prefix = data.get('prefix', 'ACT')
    code = f"{prefix}-{generate_code()}"
    
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    c.execute("INSERT INTO codes (code, duration_days) VALUES (?, ?)",
              (code, duration_days))
    conn.commit()
    conn.close()
    
    return jsonify({'code': code, 'duration_days': duration_days})

@app.route('/codes', methods=['GET'])
def get_codes():
    conn = sqlite3.connect('activation.db')
    c = conn.cursor()
    c.execute("SELECT * FROM codes ORDER BY created_at DESC")
    codes = c.fetchall()
    conn.close()
    
    codes_list = []
    for code in codes:
        codes_list.append({
            'id': code[0],
            'code': code[1],
            'created_at': code[2],
            'duration_days': code[3],
            'is_active': bool(code[4]),
            'device_id': code[5],
            'used_at': code[6]
        })
    
    return jsonify(codes_list)

if name == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)