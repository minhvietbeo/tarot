from flask import Flask, render_template, jsonify, session, request # type: ignore
from werkzeug.security import generate_password_hash, check_password_hash # Đã thêm check_password_hash
import pyodbc # type: ignore

app = Flask(__name__, template_folder='tarot', static_folder='tarot', static_url_path='')
app.secret_key = 'mot_chuoi_bi_mat_bat_ky'

def get_db_connection():
    """Hàm tạo kết nối tới SQL Server"""
    server = 'LAPTOP-BD3BQ9OJ'
    database = 'tarot'
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
    return pyodbc.connect(conn_str)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/pages/detail/detail.html')
def detail():
    return render_template('pages/detail/detail.html')

@app.route('/api/user')
def get_user():
    if 'user' in session:
        return jsonify({"user": session['user']})
    return jsonify({"user": None})

# API ĐĂNG NHẬP
@app.route('/api/login', methods=['POST'])
def api_login():
    """API kiểm tra tài khoản và mật khẩu từ Database"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"success": False, "error": "Vui lòng nhập đầy đủ tài khoản và mật khẩu!"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT username, password_hash FROM users WHERE username = ?", (username,))
        user_record = cursor.fetchone()

        if user_record:
            db_username = user_record[0]
            db_password_hash = user_record[1]

            if check_password_hash(db_password_hash, password):
                session['user'] = db_username # Lưu session
                cursor.close()
                conn.close()
                return jsonify({"success": True})
        
        cursor.close()
        conn.close()
        return jsonify({"success": False, "error": "Tên đăng nhập hoặc mật khẩu không chính xác!"}), 401

    except Exception as err:
        print(f"\n[LỖI ĐĂNG NHẬP] {err}\n")
        return jsonify({"success": False, "error": "Lỗi kết nối cơ sở dữ liệu!"}), 500

# API ĐĂNG KÝ
@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')

    if not username or not email or not password:
        return jsonify({"success": False, "error": "Vui lòng nhập đầy đủ thông tin!"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return jsonify({"success": False, "error": "Tên đăng nhập hoặc Email đã tồn tại!"}), 400

        hashed_pw = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
        
        cursor.close()
        conn.close()

        return jsonify({"success": True})

    except Exception as err:
        print(f"\n[LỖI ĐĂNG KÝ] {err}\n")
        return jsonify({"success": False, "error": "Lỗi máy chủ cơ sở dữ liệu!"}), 500

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/test_login/<username>')
def test_login(username):
    session['user'] = username
    return f"Đã đăng nhập: {username}. Quay lại trang chủ nhé!"

@app.route('/api/draw')
def draw_card():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT TOP 1 name AS category, image_url AS img, description AS message FROM cards ORDER BY NEWID()")
    row = cursor.fetchone()
    
    if row:
        columns = [column[0] for column in cursor.description]
        card = dict(zip(columns, row))
        
        cursor.close()
        conn.close()
        return jsonify(card)
    else:
        return jsonify({"error": "Chưa có bài trong DB"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)