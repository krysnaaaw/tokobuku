from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buku.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'bookstore/static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(app)

# ===== MODELS =====
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    
    seller = db.relationship('User', backref='books')
    category = db.relationship('Category', backref='books')
    
    # MEMPERBAIKI: Menambahkan cascade delete untuk CartItem
    cart_items = db.relationship('CartItem', backref='book', lazy=True, cascade='all, delete-orphan')
    
    # MEMPERBAIKI: Menambahkan cascade delete untuk OrderItem
    order_items = db.relationship('OrderItem', backref='book', lazy=True, cascade='all, delete-orphan')
    
    # MEMPERBAIKI: Menambahkan cascade delete untuk Wishlist
    wishlisted_by = db.relationship('Wishlist', backref='book', lazy=True, cascade='all, delete-orphan')

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    
    cart = db.relationship('Cart', backref='items')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    shipping_address = db.Column(db.Text, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='wishlists')

# ===== DISCUSSION FORUM MODELS =====
class Discussion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='discussions')
    comments = db.relationship('DiscussionComment', backref='discussion', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('DiscussionLike', backref='discussion', lazy=True, cascade='all, delete-orphan')

class DiscussionComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='discussion_comments')
    likes = db.relationship('CommentLike', backref='comment', lazy=True, cascade='all, delete-orphan')

class DiscussionLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    discussion_id = db.Column(db.Integer, db.ForeignKey('discussion.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='discussion_likes')

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('discussion_comment.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comment_likes')

# ===== INITIALIZATION =====
def initialize_database():
    """Initialize database with default data"""
    with app.app_context():
        db.create_all()
        
        # Create default categories if none exist
        if Category.query.count() == 0:
            categories = [
                Category(name='Fiksi', description='Novel fiksi dan cerita rekaan'),
                Category(name='Non-Fiksi', description='Buku berdasarkan fakta dan realita'),
                Category(name='Sains', description='Buku ilmu pengetahuan dan teknologi'),
                Category(name='Bisnis', description='Buku entrepreneurship dan manajemen'),
                Category(name='Anak-anak', description='Buku untuk anak-anak'),
            ]
            
            for category in categories:
                db.session.add(category)
            
            db.session.commit()
            print("✅ Database initialized with default categories!")

# ===== AUTH ROUTES =====
@app.route('/')
def index():
    books = Book.query.limit(8).all()
    return render_template('index.html', books=books)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            flash('Login berhasil!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Username atau password salah!', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Password tidak cocok!', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan!', 'error')
            return render_template('auth/register.html')
        
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Create cart for new user
        new_cart = Cart(user_id=new_user.id)
        db.session.add(new_cart)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('auth/register.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout berhasil!', 'success')
    return redirect(url_for('index'))

# ===== BOOK ROUTES =====
@app.route('/books')
def book_list():
    category_id = request.args.get('category_id')
    search = request.args.get('search')
    
    query = Book.query
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    
    books = query.all()
    categories = Category.query.all()
    return render_template('books/book_list.html', books=books, categories=categories)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books/book_detail.html', book=book)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        author = request.form['author']
        description = request.form['description']
        price = float(request.form['price'])
        stock = int(request.form['stock'])
        category_id = int(request.form['category_id'])
        
        # Handle image upload
        image = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image = filename
        
        new_book = Book(
            title=title,
            author=author,
            description=description,
            price=price,
            stock=stock,
            image=image,
            user_id=session['user_id'],
            category_id=category_id
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        flash('Buku berhasil ditambahkan!', 'success')
        return redirect(url_for('book_list'))
    
    categories = Category.query.all()
    return render_template('books/add_book.html', categories=categories)

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    book = Book.query.get_or_404(book_id)
    
    # Check if user owns the book or is admin
    if book.user_id != session['user_id'] and not session.get('is_admin'):
        flash('Anda tidak memiliki akses untuk mengedit buku ini!', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    if request.method == 'POST':
        book.title = request.form['title']
        book.author = request.form['author']
        book.description = request.form['description']
        book.price = float(request.form['price'])
        book.stock = int(request.form['stock'])
        book.category_id = int(request.form['category_id'])
        
        # Handle image update
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                # Delete old image if exists
                if book.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], book.image)):
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], book.image))
                
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                book.image = filename
        
        db.session.commit()
        
        flash('Informasi buku berhasil diperbarui!', 'success')
        return redirect(url_for('book_detail', book_id=book.id))
    
    categories = Category.query.all()
    return render_template('books/edit_book.html', book=book, categories=categories)

@app.route('/delete_book/<int:book_id>', methods=['POST'])
def delete_book(book_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    book = Book.query.get_or_404(book_id)
    
    # Check if user owns the book or is admin
    if book.user_id != session['user_id'] and not session.get('is_admin'):
        flash('Anda tidak memiliki akses untuk menghapus buku ini!', 'error')
        return redirect(url_for('book_detail', book_id=book_id))
    
    # Delete book image if exists
    if book.image and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], book.image)):
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], book.image))
    
    db.session.delete(book)
    db.session.commit()
    
    flash('Buku berhasil dihapus!', 'success')
    return redirect(url_for('book_list'))

@app.route('/my_books')
def my_books():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    user_books = Book.query.filter_by(user_id=session['user_id']).order_by(Book.created_at.desc()).all()
    return render_template('books/my_books.html', books=user_books)

# ===== CART ROUTES =====
@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    cart_items = []
    total = 0
    
    if cart:
        cart_items = db.session.query(CartItem, Book).join(Book).filter(CartItem.cart_id == cart.id).all()
        total = sum(item.Book.price * item.CartItem.quantity for item in cart_items)
    
    return render_template('cart/cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu!'})
    
    data = request.get_json()
    book_id = data['book_id']
    quantity = data.get('quantity', 1)
    
    book = Book.query.get(book_id)
    if not book:
        return jsonify({'success': False, 'message': 'Buku tidak ditemukan!'})
    
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    if not cart:
        cart = Cart(user_id=session['user_id'])
        db.session.add(cart)
        db.session.commit()
    
    existing_item = CartItem.query.filter_by(cart_id=cart.id, book_id=book_id).first()
    
    if existing_item:
        existing_item.quantity += quantity
    else:
        new_item = CartItem(cart_id=cart.id, book_id=book_id, quantity=quantity)
        db.session.add(new_item)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Buku berhasil ditambahkan ke keranjang!'})

@app.route('/update_cart_item/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu!'})
    
    data = request.get_json()
    action = data.get('action')
    
    cart_item = CartItem.query.get_or_404(item_id)
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    
    if not cart or cart_item.cart_id != cart.id:
        return jsonify({'success': False, 'message': 'Akses ditolak!'})
    
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 1:
        cart_item.quantity -= 1
    elif action == 'remove':
        db.session.delete(cart_item)
    
    db.session.commit()
    
    cart_items = db.session.query(CartItem, Book).join(Book).filter(CartItem.cart_id == cart.id).all()
    total = sum(item.Book.price * item.CartItem.quantity for item in cart_items)
    
    return jsonify({
        'success': True, 
        'new_quantity': cart_item.quantity if action != 'remove' else 0,
        'item_total': cart_item.book.price * cart_item.quantity if action != 'remove' else 0,
        'total': total
    })

# ===== CHECKOUT & ORDER ROUTES =====
@app.route('/checkout')
def checkout():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    cart_items = []
    total = 0
    
    if cart:
        cart_items = db.session.query(CartItem, Book).join(Book).filter(CartItem.cart_id == cart.id).all()
        total = sum(item.Book.price * item.CartItem.quantity for item in cart_items)
    
    if not cart_items:
        flash('Keranjang belanja kosong!', 'error')
        return redirect(url_for('cart'))
    
    user = User.query.get(session['user_id'])
    return render_template('cart/checkout.html', cart_items=cart_items, total=total, user=user)

@app.route('/process_checkout', methods=['POST'])
def process_checkout():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    shipping_address = request.form['shipping_address']
    payment_method = request.form['payment_method']
    notes = request.form.get('notes', '')
    
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    if not cart:
        flash('Keranjang belanja kosong!', 'error')
        return redirect(url_for('cart'))
    
    cart_items = db.session.query(CartItem, Book).join(Book).filter(CartItem.cart_id == cart.id).all()
    if not cart_items:
        flash('Keranjang belanja kosong!', 'error')
        return redirect(url_for('cart'))
    
    total = sum(item.Book.price * item.CartItem.quantity for item in cart_items)
    
    new_order = Order(
        user_id=session['user_id'],
        total_amount=total,
        shipping_address=shipping_address,
        payment_method=payment_method,
        status='pending'
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    for item in cart_items:
        order_item = OrderItem(
            order_id=new_order.id,
            book_id=item.Book.id,
            quantity=item.CartItem.quantity,
            price=item.Book.price
        )
        db.session.add(order_item)
        item.Book.stock -= item.CartItem.quantity
    
    CartItem.query.filter_by(cart_id=cart.id).delete()
    db.session.commit()
    
    flash(f'Pesanan berhasil dibuat! Order ID: #{new_order.id}', 'success')
    return redirect(url_for('order_confirmation', order_id=new_order.id))

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id'] and not session.get('is_admin'):
        flash('Akses ditolak!', 'error')
        return redirect(url_for('index'))
    
    order_items = db.session.query(OrderItem, Book).join(Book).filter(OrderItem.order_id == order_id).all()
    
    return render_template('cart/order_confirmation.html', order=order, order_items=order_items)

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    user_orders = Order.query.filter_by(user_id=session['user_id']).order_by(Order.created_at.desc()).all()
    return render_template('user/orders.html', orders=user_orders)

@app.route('/order_detail/<int:order_id>')
def order_detail(order_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != session['user_id'] and not session.get('is_admin'):
        flash('Akses ditolak!', 'error')
        return redirect(url_for('index'))
    
    order_items = db.session.query(OrderItem, Book).join(Book).filter(OrderItem.order_id == order_id).all()
    
    return render_template('user/order_detail.html', order=order, order_items=order_items)

# ===== DISCUSSION FORUM ROUTES =====
@app.route('/discussion')
def discussion_forum():
    discussions = Discussion.query.filter_by(is_public=True).order_by(Discussion.created_at.desc()).all()
    return render_template('discussion/forum.html', discussions=discussions)

@app.route('/discussion/create', methods=['GET', 'POST'])
def create_discussion():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        is_public = 'is_public' in request.form
        
        new_discussion = Discussion(
            user_id=session['user_id'],
            title=title,
            content=content,
            is_public=is_public
        )
        
        db.session.add(new_discussion)
        db.session.commit()
        
        flash('Diskusi berhasil dibuat!', 'success')
        return redirect(url_for('discussion_detail', discussion_id=new_discussion.id))
    
    return render_template('discussion/create.html')

@app.route('/discussion/<int:discussion_id>')
def discussion_detail(discussion_id):
    discussion = Discussion.query.get_or_404(discussion_id)
    
    if not discussion.is_public and discussion.user_id != session.get('user_id'):
        flash('Diskusi ini bersifat private!', 'error')
        return redirect(url_for('discussion_forum'))
    
    comments = DiscussionComment.query.filter_by(discussion_id=discussion_id).order_by(DiscussionComment.created_at.asc()).all()
    
    user_liked = False
    if 'user_id' in session:
        user_liked = DiscussionLike.query.filter_by(
            user_id=session['user_id'], 
            discussion_id=discussion_id
        ).first() is not None
    
    return render_template('discussion/detail.html', 
                         discussion=discussion, 
                         comments=comments,
                         user_liked=user_liked)

@app.route('/discussion/<int:discussion_id>/comment', methods=['POST'])
def add_comment(discussion_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu!'})
    
    discussion = Discussion.query.get_or_404(discussion_id)
    
    if not discussion.is_public and discussion.user_id != session.get('user_id'):
        return jsonify({'success': False, 'message': 'Akses ditolak!'})
    
    content = request.form['content']
    
    new_comment = DiscussionComment(
        user_id=session['user_id'],
        discussion_id=discussion_id,
        content=content
    )
    
    db.session.add(new_comment)
    db.session.commit()
    
    flash('Komentar berhasil ditambahkan!', 'success')
    return redirect(url_for('discussion_detail', discussion_id=discussion_id))

@app.route('/discussion/<int:discussion_id>/like', methods=['POST'])
def like_discussion(discussion_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu!'})
    
    discussion = Discussion.query.get_or_404(discussion_id)
    
    existing_like = DiscussionLike.query.filter_by(
        user_id=session['user_id'],
        discussion_id=discussion_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        action = 'unlike'
    else:
        new_like = DiscussionLike(
            user_id=session['user_id'],
            discussion_id=discussion_id
        )
        db.session.add(new_like)
        action = 'like'
    
    db.session.commit()
    
    like_count = DiscussionLike.query.filter_by(discussion_id=discussion_id).count()
    
    return jsonify({
        'success': True,
        'action': action,
        'like_count': like_count
    })

@app.route('/comment/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Silakan login terlebih dahulu!'})
    
    comment = DiscussionComment.query.get_or_404(comment_id)
    
    existing_like = CommentLike.query.filter_by(
        user_id=session['user_id'],
        comment_id=comment_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
        action = 'unlike'
    else:
        new_like = CommentLike(
            user_id=session['user_id'],
            comment_id=comment_id
        )
        db.session.add(new_like)
        action = 'like'
    
    db.session.commit()
    
    like_count = CommentLike.query.filter_by(comment_id=comment_id).count()
    
    return jsonify({
        'success': True,
        'action': action,
        'like_count': like_count
    })

@app.route('/my_discussions')
def my_discussions():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    discussions = Discussion.query.filter_by(user_id=session['user_id']).order_by(Discussion.created_at.desc()).all()
    return render_template('discussion/my_discussions.html', discussions=discussions)

@app.route('/discussion/<int:discussion_id>/delete', methods=['POST'])
def delete_discussion(discussion_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    discussion = Discussion.query.get_or_404(discussion_id)
    
    if discussion.user_id != session['user_id'] and not session.get('is_admin'):
        flash('Anda tidak memiliki akses untuk menghapus diskusi ini!', 'error')
        return redirect(url_for('discussion_detail', discussion_id=discussion_id))
    
    db.session.delete(discussion)
    db.session.commit()
    
    flash('Diskusi berhasil dihapus!', 'success')
    return redirect(url_for('discussion_forum'))

# ===== PROFILE & WISHLIST ROUTES =====
@app.route('/profile')
def profile():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('user/profile.html', user=user)

@app.route('/edit_profile', methods=['POST'])
def edit_profile():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    user.email = request.form['email']
    
    db.session.commit()
    flash('Profil berhasil diperbarui!', 'success')
    return redirect(url_for('profile'))

@app.route('/wishlist')
def wishlist():
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    wishlist_items = Wishlist.query.filter_by(user_id=session['user_id']).all()
    return render_template('user/wishlist.html', wishlist_items=wishlist_items)

@app.route('/add_to_wishlist/<int:book_id>')
def add_to_wishlist(book_id):
    if 'user_id' not in session:
        flash('Silakan login terlebih dahulu!', 'error')
        return redirect(url_for('login'))
    
    existing = Wishlist.query.filter_by(user_id=session['user_id'], book_id=book_id).first()
    if not existing:
        new_wishlist = Wishlist(user_id=session['user_id'], book_id=book_id)
        db.session.add(new_wishlist)
        db.session.commit()
        flash('Buku berhasil ditambahkan ke wishlist!', 'success')
    else:
        flash('Buku sudah ada di wishlist!', 'info')
    
    return redirect(request.referrer or url_for('index'))

# ===== ADMIN DASHBOARD ROUTES =====
@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    # Get statistics
    total_users = User.query.count()
    total_books = Book.query.count()
    total_orders = Order.query.count()
    total_discussions = Discussion.query.count()
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Revenue calculation (simple version)
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_books=total_books,
                         total_orders=total_orders,
                         total_discussions=total_discussions,
                         total_revenue=total_revenue,
                         recent_orders=recent_orders,
                         recent_users=recent_users)

@app.route('/admin/users')
def admin_users():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/books')
def admin_books():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    books = Book.query.order_by(Book.created_at.desc()).all()
    return render_template('admin/books.html', books=books)

@app.route('/admin/orders')
def admin_orders():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)

@app.route('/admin/discussions')
def admin_discussions():
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    discussions = Discussion.query.order_by(Discussion.created_at.desc()).all()
    return render_template('admin/discussions.html', discussions=discussions)

@app.route('/admin/user/<int:user_id>/toggle_admin', methods=['POST'])
def toggle_admin(user_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    action = "dijadikan admin" if user.is_admin else "dihapus dari admin"
    flash(f'User {user.username} berhasil {action}!', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/order/<int:order_id>/update_status', methods=['POST'])
def update_order_status(order_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    order = Order.query.get_or_404(order_id)
    new_status = request.form['status']
    order.status = new_status
    db.session.commit()
    
    flash(f'Status order #{order.id} berhasil diupdate menjadi {new_status}!', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/admin/book/<int:book_id>/delete', methods=['POST'])
def admin_delete_book(book_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    
    flash('Buku berhasil dihapus!', 'success')
    return redirect(url_for('admin_books'))

@app.route('/admin/discussion/<int:discussion_id>/delete', methods=['POST'])
def admin_delete_discussion(discussion_id):
    if 'user_id' not in session or not session.get('is_admin'):
        flash('Akses ditolak! Hanya admin yang bisa mengakses.', 'error')
        return redirect(url_for('index'))
    
    discussion = Discussion.query.get_or_404(discussion_id)
    db.session.delete(discussion)
    db.session.commit()
    
    flash('Diskusi berhasil dihapus!', 'success')
    return redirect(url_for('admin_discussions'))

# ===== API ROUTES =====
@app.route('/api/cart/count')
def api_cart_count():
    if 'user_id' not in session:
        return jsonify({'count': 0})
    
    cart = Cart.query.filter_by(user_id=session['user_id']).first()
    if not cart:
        return jsonify({'count': 0})
    
    count = CartItem.query.filter_by(cart_id=cart.id).count()
    return jsonify({'count': count})

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)