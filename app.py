from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "rahasia_super"
app.debug = True

# --- Koneksi ke Database ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # ubah jika pakai user lain
        password="",       # isi password MySQL jika ada
        database="db_buku"
    )

# === Halaman Login (tampil form) ===
@app.route('/', methods=['GET'])
def home():
    return render_template('login.html')

# === Proses Login (POST) ===
@app.route('/login', methods=['POST'])
def login():
    # Ambil data dari form
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')

    if not username or not password:
        flash("Username dan password wajib diisi.", "danger")
        return redirect(url_for('home'))

    try:
        db = get_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
    except Error as e:
        # Kalau gagal koneksi/eksekusi SQL, beri tahu user (tidak menampilkan detail error ke user)
        app.logger.error("Database error saat login: %s", e)
        flash("Gagal terhubung ke database. Coba lagi nanti.", "danger")
        return redirect(url_for('home'))
    finally:
        try:
            cursor.close()
            db.close()
        except:
            pass

    if user:
        flash(f"Selamat datang, {username}!", "success")
        return redirect(url_for('dashboard'))
    else:
        flash("User tidak ditemukan. Silakan daftar terlebih dahulu.", "danger")
        return redirect(url_for('home'))

# === Halaman Register (GET+POST) ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Ambil data dari form (pastikan name pada input sama dengan ini)
        nama = request.form.get('nama_lengkap', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        email = request.form.get('email', '').strip()
        whatsapp = request.form.get('whatsapp', '').strip()

        # Validasi sederhana
        if not username or not password:
            flash("Username dan password wajib diisi.", "danger")
            return redirect(url_for('register'))
        if len(password) < 6:
            flash("Password minimal 6 karakter.", "danger")
            return redirect(url_for('register'))

        try:
            db = get_connection()
            cursor = db.cursor(dictionary=True)

            # cek apakah username sudah ada
            cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
            if cursor.fetchone():
                flash("Username sudah digunakan, coba yang lain.", "danger")
                return redirect(url_for('register'))

            # insert data (tanpa hashing sesuai permintaan)
            cursor.execute(
                "INSERT INTO users (nama_lengkap, username, password, email, whatsapp) VALUES (%s, %s, %s, %s, %s)",
                (nama or None, username, password, email or None, whatsapp or None)
            )
            db.commit()
            flash("Akun berhasil dibuat! Silakan login.", "success")
            return redirect(url_for('home'))

        except Error as e:
            app.logger.error("Database error saat register: %s", e)
            flash("Gagal menyimpan data. Coba lagi nanti.", "danger")
            return redirect(url_for('register'))
        finally:
            try:
                cursor.close()
                db.close()
            except:
                pass

    # GET -> tampilkan form register
    return render_template('register.html')

# === Dashboard sederhana ===
@app.route('/home', methods=['GET'])
def dashboard():
    return render_template('home.html')

if __name__ == '__main__':
    # Jalankan di 127.0.0.1:5000 (default). Pastikan MySQL berjalan di XAMPP.
    app.run(debug=True)