from flask import Flask, render_template, request, redirect, url_for, flash, session
import mysql.connector
from mysql.connector import Error
from functools import wraps
import logging
import os
from werkzeug.utils import secure_filename
from datetime import datetime  # Import untuk penanganan tanggal

# ============================
#   KONFIGURASI APLIKASI
# ============================
app = Flask(__name__)
app.secret_key = "rahasia_super"  # Ganti dengan secret key yang kuat untuk production
app.debug = True

# --- Upload File ---
UPLOAD_FOLDER = 'static/image/cover'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- Logging ---
logging.basicConfig(level=logging.DEBUG)

# ============================
#   HELPER FUNCTIONS
# ============================
def get_connection():
    """Membuat koneksi ke database MySQL"""
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_buku"
    )

def allowed_file(filename):
    """Cek ekstensi file yang diperbolehkan"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator untuk memastikan pengguna sudah login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            flash('Anda harus login untuk mengakses halaman ini.', 'warning')
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# ============================
#   ROUTES
# ============================

# --- DASHBOARD ---
@app.route('/', methods=['GET'])
def dashboard():
    db = cursor = None
    buku_list = []
    try:
        db = get_connection()
        # Menggunakan dictionary=True agar hasil query berupa dict
        cursor = db.cursor(dictionary=True) 
        # Ambil kolom yang diperlukan (pastikan id_buku sesuai dengan nama kolom di DB)
        cursor.execute("SELECT id_buku, judul, penulis, harga, gambar FROM produk_buku ORDER BY id_buku DESC LIMIT 12")
        buku_list = cursor.fetchall()
    except Error as e:
        app.logger.error("Database error saat ambil daftar buku: %s", e)
        flash("Gagal memuat daftar buku. Coba lagi nanti.", "danger")
    finally:
        if cursor: cursor.close()
        if db: db.close()

    # Mengirim buku_list ke home.html
    return render_template('home.html', buku_list=buku_list)

# --- LOGIN ---
@app.route('/login_page', methods=['GET'])
def login_page():
    if session.get('logged_in'):
        flash("Anda sudah login.", "info")
        return redirect(url_for('profile'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash("Username dan password wajib diisi.", "danger")
        return redirect(url_for('login_page'))

    db = cursor = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cursor.fetchone()
    except Error as e:
        app.logger.error("Database error saat login: %s", e)
        flash("Gagal terhubung ke database. Coba lagi nanti.", "danger")
        return redirect(url_for('login_page'))
    finally:
        if cursor: cursor.close()
        if db: db.close()

    if user:
        session['logged_in'] = True
        session['user_id'] = user['id']
        session['username'] = user['username']
        flash(f"Selamat datang, {username}!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("Username atau password salah. Coba lagi.", "danger")
        return redirect(url_for('login_page'))


# --- LOGOUT ---
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("Anda berhasil logout.", "success")
    return redirect(url_for('dashboard'))


# --- PROFIL ---
@app.route('/profile', methods=['GET'])
@login_required
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash("Sesi pengguna tidak ditemukan. Silakan login ulang.", "danger")
        return redirect(url_for('login_page'))

    db = cursor = None
    user = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, nama_lengkap, username, email, whatsapp FROM users WHERE id=%s",
            (user_id,)
        )
        user = cursor.fetchone()
    except Error as e:
        app.logger.error("Database error saat ambil profil: %s", e)
        flash("Gagal memuat profil. Coba lagi nanti.", "danger")
        return render_template('home.html')
    finally:
        if cursor: cursor.close()
        if db: db.close()

    if user:
        return render_template('profile.html', user=user)
    else:
        flash("Data pengguna tidak valid. Silakan login ulang.", "danger")
        session.clear()
        return redirect(url_for('login_page'))


# --- REGISTER ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nama = request.form.get('nama_lengkap', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()

        if not username or not password:
            flash("Username dan password wajib diisi.", "danger")
            return redirect(url_for('register'))
        if len(password) < 6:
            flash("Password minimal 6 karakter.", "danger")
            return redirect(url_for('register'))

        db = cursor = None
        try:
            db = get_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                flash("Username sudah digunakan, coba yang lain.", "danger")
                return redirect(url_for('register'))

            cursor.execute(
                "INSERT INTO users (nama_lengkap, username, password, email, whatsapp) VALUES (%s, %s, %s, %s, %s)",
                (nama or None, username, password, email or None, whatsapp or None)
            )
            db.commit()
            flash("Akun berhasil dibuat! Silakan login.", "success")
            return redirect(url_for('login_page'))
        except Error as e:
            app.logger.error("Database error saat register: %s", e)
            flash("Gagal menyimpan data. Coba lagi nanti.", "danger")
            return redirect(url_for('register'))
        finally:
            if cursor: cursor.close()
            if db: db.close()

    return render_template('register.html')


# --- DETAIL BUKU ---
@app.route('/buku/<int:buku_id>', methods=['GET'])
def detail_buku(buku_id):
    db = cursor = None
    buku = None
    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM produk_buku WHERE id_buku=%s", (buku_id,))
        buku = cursor.fetchone()
        if not buku:
            flash("Buku tidak ditemukan.", "danger")
            return redirect(url_for('dashboard'))
    except Error as e:
        app.logger.error("Database error saat ambil buku: %s", e)
        flash("Terjadi kesalahan, coba lagi nanti.", "danger")
        return redirect(url_for('dashboard'))
    finally:
        if cursor: cursor.close()
        if db: db.close()

    return render_template('isibuku.html', buku=buku)


# --- UPLOAD BUKU ---
@app.route('/upload_buku', methods=['GET', 'POST'])
@login_required
def upload_buku():
    if request.method == 'POST':
        # Ambil data dari form
        judul = request.form.get('judul', '').strip()
        penulis = request.form.get('penulis', '').strip()
        penerbit = request.form.get('penerbit', '').strip()
        isbn = request.form.get('isbn', '').strip()
        tanggal_terbit_str = request.form.get('tanggal_terbit', '').strip()
        kategori = request.form.get('kategori', '').strip()
        harga_str = request.form.get('harga', '').strip()
        stok_str = request.form.get('stok', '').strip()
        deskripsi = request.form.get('deskripsi', '').strip()
        bahasa = request.form.get('bahasa', '').strip()
        halaman_str = request.form.get('jml_halaman', '').strip()
        panjang_str = request.form.get('panjang', '').strip()
        lebar_str = request.form.get('lebar', '').strip()

        # Validasi kolom NOT NULL
        if not judul or not penulis or not penerbit or not harga_str or not stok_str:
            flash("Judul, Penulis, Penerbit, Harga, dan Stok wajib diisi.", "danger")
            return redirect(url_for('upload_buku'))

        # File cover
        if 'cover_file' not in request.files or request.files['cover_file'].filename == '':
            flash("Cover buku wajib diunggah.", "danger")
            return redirect(url_for('upload_buku'))

        file = request.files['cover_file']
        filename = None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            try:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                app.logger.error("Gagal menyimpan file cover: %s", e)
                flash("Gagal menyimpan file cover.", "danger")
                return redirect(url_for('upload_buku'))
        else:
            flash("Format file cover tidak didukung (PNG, JPG, JPEG).", "danger")
            return redirect(url_for('upload_buku'))

        # Konversi tipe data
        try:
            harga = int(harga_str)
            stok = int(stok_str)
            halaman = int(halaman_str) if halaman_str.isdigit() else None
            panjang = float(panjang_str) if panjang_str else None
            lebar = float(lebar_str) if lebar_str else None
            tanggal_terbit = tanggal_terbit_str if tanggal_terbit_str else None
        except ValueError:
            flash("Harga, Stok, Halaman, Panjang, dan Lebar harus berupa angka yang valid.", "danger")
            if filename and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('upload_buku'))

        # Simpan ke database
        db = cursor = None
        try:
            db = get_connection()
            cursor = db.cursor()
            sql = """
                INSERT INTO produk_buku 
                (judul, penulis, penerbit, isbn, tanggal_terbit, kategori, bahasa, harga, stok, halaman, lebar, panjang, deskripsi, gambar)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                judul, penulis, penerbit, isbn or None, tanggal_terbit, kategori or None,
                bahasa or None, harga, stok, halaman, lebar, panjang, deskripsi or None, filename
            ))
            db.commit()
            flash(f"Buku '{judul}' berhasil diunggah!", "success")
            return redirect(url_for('dashboard'))
        except Error as e:
            app.logger.error("Database error saat upload buku: %s", e)
            if filename and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash(f"Gagal menyimpan data buku ke database. Detail error: {e.msg}", "danger")
            return redirect(url_for('upload_buku'))
        finally:
            if cursor: cursor.close()
            if db: db.close()

    return render_template('uploadbuku.html')


# ============================
#   MAIN
# ============================
if __name__ == '__main__':
    app.run(debug=True)
