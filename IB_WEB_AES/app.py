# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit, disconnect
from datetime import datetime
import logging
import os
import sys # Import sys để cấu hình StreamHandler cho logging
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

# --- Cấu hình ứng dụng và Logging ---
app = Flask(__name__)
# Đã tạo một SECRET_KEY ngẫu nhiên.
# Trong môi trường production, bạn nên lưu khóa này trong biến môi trường hoặc file cấu hình riêng.
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app.db' # Sử dụng SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo các tiện ích mở rộng
socketio = SocketIO(app, cors_allowed_origins="*") # Cho phép tất cả các nguồn gốc trong môi trường dev
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' # Trang chuyển hướng nếu người dùng chưa đăng nhập

# Cấu hình logging
# Thay đổi level=logging.DEBUG để thấy nhiều thông tin gỡ lỗi hơn
logging.basicConfig(level=logging.DEBUG, # Đã đổi thành DEBUG để xem chi tiết hơn
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log", encoding='utf-8'), # Ghi log ra file với UTF-8
                        # Cấu hình StreamHandler để ghi ra console với mã hóa UTF-8, khắc phục UnicodeEncodeError
                        logging.StreamHandler(sys.stdout) # Chỉ định encoding trực tiếp được loại bỏ để tương thích rộng hơn
                    ])

# --- Models Cơ sở dữ liệu ---

# Model User cho Flask-Login
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    # Quan hệ với tin nhắn gửi đi và nhận về (tùy chọn nhưng hữu ích)
    messages_sent = db.relationship('Message', foreign_keys='Message.user_id', backref='sender', lazy=True)
    messages_received = db.relationship('Message', foreign_keys='Message.receiver_id', backref='receiver', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

# Model Message để lưu lịch sử chat
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # ID của người gửi
    sender_username = db.Column(db.String(100), nullable=False) # Username của người gửi (để tiện tra cứu)
    encrypted_content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    room = db.Column(db.String(50), nullable=True) # Tên phòng (nếu là tin nhắn công khai)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # ID của người nhận (nếu là tin nhắn riêng)

    def __repr__(self):
        msg_type = "public" if self.room else "private"
        if msg_type == "private" and self.receiver:
            return f"<Message {self.id} from {self.sender_username} to {self.receiver.username} at {self.timestamp}>"
        return f"<Message {self.id} from {self.sender_username} in room '{self.room}' at {self.timestamp}>"

# --- Flask-Login User Loader ---
# Hàm này được Flask-Login sử dụng để tải một đối tượng User từ ID người dùng
@login_manager.user_loader
def load_user(user_id):
    # Sử dụng Session.get() thay vì Query.get() theo khuyến nghị của SQLAlchemy 2.0
    return db.session.get(User, int(user_id))

# --- Quản lý kết nối Socket.IO đang hoạt động (vẫn cần để gửi real-time nếu user online) ---
active_users_sids = {} # {user_id: [sid1, sid2, ...]}
sid_to_user_id = {} # {sid: user_id}

# --- Routes cho Đăng ký, Đăng nhập, Đăng xuất ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Tên người dùng đã tồn tại. Vui lòng chọn tên khác.', 'danger')
            return render_template('register.html')
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Tên người dùng hoặc mật khẩu không hợp lệ.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Bạn đã đăng xuất.', 'info')
    return redirect(url_for('login'))

# --- Route chính cho trang chat ---
@app.route('/')
@login_required
def index():
    # Lấy TẤT CẢ người dùng đã đăng ký để hiển thị danh sách chọn
    all_users = User.query.all()
    # Loại bỏ chính người dùng hiện tại khỏi danh sách
    other_users = [user.username for user in all_users if user.id != current_user.id]
    return render_template('index.html', username=current_user.username, all_users=other_users)

# --- Xử lý sự kiện Socket.IO ---

@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        user_id = current_user.id
        username = current_user.username
        sid = request.sid

        if user_id not in active_users_sids:
            active_users_sids[user_id] = []
        active_users_sids[user_id].append(sid)
        sid_to_user_id[sid] = user_id

        logging.info(f'User {username} (ID: {user_id}) connected with SID: {sid}. Total SIDs for user: {len(active_users_sids[user_id])}')
        logging.debug(f"DEBUG Connect: active_users_sids: {active_users_sids}")
        logging.debug(f"DEBUG Connect: sid_to_user_id: {sid_to_user_id}")

        # Gửi tin nhắn chào mừng
        emit('status', {'msg': f'Chào mừng, {username}!'}, room=sid)

        # Lấy lịch sử tin nhắn liên quan đến người dùng này
        messages = db.session.query(Message).filter(
            (Message.room == 'general') |
            ((Message.user_id == current_user.id) | (Message.receiver_id == current_user.id))
        ).order_by(Message.timestamp.asc()).all()

        history = []
        for msg in messages:
            msg_data = {
                'sender': msg.sender_username,
                'content': msg.encrypted_content,
                'timestamp': msg.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'type': 'public' if msg.room == 'general' else 'private'
            }
            if msg.receiver_id:
                receiver_user = db.session.get(User, msg.receiver_id)
                if receiver_user:
                    msg_data['receiver'] = receiver_user.username
            history.append(msg_data)
        emit('history', {'messages': history}, room=sid)
    else:
        logging.warning(f'Client không được xác thực kết nối: {request.sid}. Ngắt kết nối.')
        disconnect(sid=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    if sid in sid_to_user_id:
        user_id = sid_to_user_id[sid]
        username = db.session.get(User, user_id).username if db.session.get(User, user_id) else "Unknown"

        if user_id in active_users_sids and sid in active_users_sids[user_id]:
            active_users_sids[user_id].remove(sid)
            if not active_users_sids[user_id]:
                del active_users_sids[user_id]
                logging.info(f'User {username} (ID: {user_id}) đã offline.')
            else:
                logging.info(f'User {username} (ID: {user_id}) ngắt kết nối một SID. SIDs còn lại: {len(active_users_sids[user_id])}')

            del sid_to_user_id[sid]
            logging.debug(f"DEBUG Disconnect: active_users_sids: {active_users_sids}")
            logging.debug(f"DEBUG Disconnect: sid_to_user_id: {sid_to_user_id}")
        else:
            logging.warning(f'SID {sid} được tìm thấy trong sid_to_user_id nhưng không trong active_users_sids. Trạng thái không nhất quán.')
    else:
        logging.info(f'Client (SID: {sid}) ngắt kết nối (không xác thực hoặc không rõ).')


@socketio.on('send_message')
@login_required
def handle_message(data):
    encrypted_message = data.get('message')
    message_type = data.get('type', 'public')
    recipient_username = data.get('recipient_username')
    room = data.get('room', 'general')

    sender_user = current_user

    if not encrypted_message:
        logging.warning(f'Nhận được tin nhắn rỗng từ {sender_user.username}')
        return

    receiver_user_id = None
    receiver_username = None
    if message_type == 'private' and recipient_username:
        recipient_user = User.query.filter_by(username=recipient_username).first()
        if not recipient_user:
            logging.warning(f'Không tìm thấy người nhận: {recipient_username} từ {sender_user.username}')
            emit('status', {'msg': f'Lỗi: Người dùng "{recipient_username}" không tìm thấy.'}, room=request.sid)
            return
        receiver_user_id = recipient_user.id
        receiver_username = recipient_user.username

        if sender_user.id == receiver_user_id:
            emit('status', {'msg': 'Không thể gửi tin nhắn riêng cho chính bạn.'}, room=request.sid)
            return

    new_message = Message(
        user_id=sender_user.id,
        sender_username=sender_user.username,
        encrypted_content=encrypted_message,
        room=room if message_type == 'public' else None,
        receiver_id=receiver_user_id
    )
    db.session.add(new_message)
    db.session.commit()
    logging.info(f'Tin nhắn đã được ghi vào DB từ {sender_user.username}. Loại: {message_type}')

    message_data = {
        'sender': sender_user.username,
        'message': encrypted_message,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'type': message_type
    }

    if message_type == 'public':
        logging.info(f'Phát sóng tin nhắn công khai vào phòng {room}.')
        emit('receive_message', message_data, room=room)
    elif message_type == 'private' and receiver_user_id:
        logging.info(f'Gửi tin nhắn riêng tư từ {sender_user.username} tới {receiver_username}.')
        message_data['receiver'] = receiver_username

        # Gửi tới tất cả các SID của người nhận nếu họ online
        if receiver_user_id in active_users_sids:
            for sid in active_users_sids[receiver_user_id]:
                emit('receive_message', message_data, room=sid)

        # Gửi tới tất cả các SID của người gửi (nếu có nhiều tab đang mở)
        if sender_user.id in active_users_sids:
            for sid in active_users_sids[sender_user.id]:
                # Đảm bảo không gửi lại tin nhắn nếu SID hiện tại là của người nhận
                # Dù đã ngăn gửi cho chính mình, nhưng cần thận trọng
                if sid == request.sid and sid_to_user_id.get(sid) == receiver_user_id:
                    continue
                emit('receive_message', message_data, room=sid)


# --- Khởi chạy ứng dụng ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if not User.query.filter_by(username='testuser').first():
            test_user = User(username='testuser')
            test_user.set_password('testpassword')
            db.session.add(test_user)
            db.session.commit()
            logging.info('Đã tạo người dùng mặc định: testuser/testpassword')
        
        if not User.query.filter_by(username='user2').first():
            user2 = User(username='user2')
            user2.set_password('password2')
            db.session.add(user2)
            db.session.commit()
            logging.info('Đã tạo người dùng mặc định: user2/password2')
        
        if not User.query.filter_by(username='user3').first():
            user3 = User(username='user3')
            user3.set_password('password3')
            db.session.add(user3)
            db.session.commit()
            logging.info('Đã tạo người dùng mặc định: user3/password3')

    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)