from flask import Flask, render_template, jsonify, session
import pyodbc # Thư viện SQL Server

app = Flask(__name__, template_folder='tarot', static_folder='tarot', static_url_path='')
app.secret_key = 'mot_chuoi_bi_mat_bat_ky'

# ==========================================
# CẤU HÌNH KẾT NỐI SQL SERVER
# ==========================================
def get_db_connection():
    """Hàm tạo kết nối tới SQL Server bằng SQL Server Authentication"""
    
    server = 'LAPTOP-BD3BQ9OJ'
    database = 'tarot'
    
    # THÊM TÀI KHOẢN VÀ MẬT KHẨU SQL SERVER CỦA BẠN VÀO ĐÂY
    username = 'sa'                  # Thường mặc định là 'sa' (System Administrator)
    password = '12345678' # Thay bằng mật khẩu SQL Server của bạn
    
    # Chuỗi kết nối dùng SQL Server Authentication
    conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'
    
    return pyodbc.connect(conn_str)
# ==========================================
# ROUTE GIAO DIỆN & ĐĂNG NHẬP
# ==========================================
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

@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('user', None)
    return jsonify({"success": True})

@app.route('/test_login/<username>')
def test_login(username):
    session['user'] = username
    return f"Đã đăng nhập: {username}. Quay lại trang chủ nhé!"

# ==========================================
# API RÚT BÀI TỪ SQL SERVER
# ==========================================
@app.route('/api/draw')
def draw_card():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Lấy NGẪU NHIÊN 1 lá bài (SQL Server dùng NEWID)
        cursor.execute("SELECT TOP 1 category, img, message FROM cards ORDER BY NEWID()")
        row = cursor.fetchone()
        
        if row:
            # pyodbc trả về Tuple, ta cần ép về dạng Dictionary (JSON) cho Front-end đọc được
            columns = [column[0] for column in cursor.description]
            card = dict(zip(columns, row))
            
            cursor.close()
            conn.close()
            return jsonify(card)
        else:
            return jsonify({"error": "Chưa có bài trong DB"}), 404

    except Exception as err:
        print(f"LỖI DATABASE: {err}")
        return jsonify({"error": "Lỗi kết nối vũ trụ (DB)"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)