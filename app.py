from flask import Flask, render_template, jsonify, session, request # type: ignore
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

@app.route('/api/login', methods=['POST'])
def api_login():
    """API nhận dữ liệu từ form login.html gửi lên"""
    data = request.json
    username = data.get('username')
    
    if username:
        session['user'] = username
        return jsonify({"success": True})
        
    return jsonify({"success": False, "error": "Vui lòng nhập tên đăng nhập!"}), 400

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/test_login/<username>')
def test_login(username):
    session['user'] = username
    return f"Đã đăng nhập: {username}. Quay lại trang chủ nhé!"

@app.route('/api/draw')
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