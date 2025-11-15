from flask import Flask, render_template, request, url_for, send_from_directory, session, redirect, jsonify
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from functools import wraps, lru_cache
from urllib.parse import unquote


from static.py.database import db
app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
DEFAULT_BOOK_COVER = 'fs_book_cover-5f4eddfb.png'
IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
ALLOWED_EXTENSIONS = {'txt', 'csv'}
UPLOAD_FOLDER = r'C:\Users\pc\Desktop\shin\webdocsach\data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ============ DATABASE ============
def normalize_user(user_data):
    """Chuyển đổi dữ liệu user từ Supabase thành format chuẩn"""
    try:
        # Parse favorite_books nếu là string
        favorite_books = user_data.get('favorite_books', [])
        if isinstance(favorite_books, str):
            if favorite_books.strip() == '[]' or favorite_books.strip() == '':
                favorite_books = []
            else:
                import json
                favorite_books = json.loads(favorite_books)
        
        # Parse borrowed_books
        borrowed_books = user_data.get('borrowed_books', [])
        if isinstance(borrowed_books, str):
            import json
            borrowed_books = json.loads(borrowed_books) if borrowed_books.strip() else []
        
        return {
            'password': user_data.get('password', 'password123'),
            'name': user_data.get('name', ''),
            'email': user_data.get('email', ''),
            'phone': user_data.get('phone', ''),
            'borrowed_books': borrowed_books if isinstance(borrowed_books, list) else [],
            'favorite_books': favorite_books if isinstance(favorite_books, list) else [],
            'borrow_limit': user_data.get('borrow_limit', 5)
        }
    except Exception as e:
        print(f"❌ Lỗi normalize user: {str(e)}")
        return {
            'password': 'password123',
            'name': user_data.get('name', ''),
            'email': user_data.get('email', ''),
            'phone': user_data.get('phone', ''),
            'borrowed_books': [],
            'favorite_books': [],
            'borrow_limit': 5
        }

# ============ LOAD USERS FROM SUPABASE ============

def load_users_from_supabase():
    """Load users từ Supabase và normalize"""
    try:
        from static.py.database import db
        
        users_list = db().get_all_users_list()
        normalized_users = {}
        
        for user in users_list:
            card_id = user.get('card_id')
            if card_id:
                normalized_users[card_id] = normalize_user(user)
        
        print(f"✅ Loaded {len(normalized_users)} users từ Supabase")
        return normalized_users
    except Exception as e:
        print(f"❌ Lỗi load users: {str(e)}")
        return {}

# ============ DATABASE ============

ADMIN_CREDENTIALS = {
    'admin': 'admin',
    'admin2': 'shinsad'
}

# Load users từ Supabase (hoặc dùng fallback)
users_db = load_users_from_supabase()
if not users_db:
    print("⚠️ Không load được users từ Supabase, dùng fallback data")
    users_db = {
        'TV001': {
            'password': 'password123',
            'name': 'Nguyễn Văn A',
            'email': 'user1@example.com',
            'phone': '0123456789',
            'borrowed_books': [],
            'favorite_books': [],
            'borrow_limit': 5
        },
        'TV002': {
            'password': 'password456',
            'name': 'Trần Thị B',
            'email': 'user2@example.com',
            'phone': '0987654321',
            'borrowed_books': [],
            'favorite_books': [],
            'borrow_limit': 5
        }
    }
# ============ CATEGORIES ============
CATEGORIES = {
    "Sách giáo khóa": ["Lớp 1", "Lớp 2", "Lớp 3", "Lớp 4", "Lớp 5"],
    "Sách giáo viên": ["Lớp 1", "Lớp 2", "Lớp 3", "Lớp 4", "Lớp 5"],
    "Truyện": ["Truyện cổ tích", "Truyện hiện đại", "Truyện dạy bảo", "Truyện hành động"],
    "Sách tham khảo": ["Toán học", "Tiếng Việt", "Tiếng Anh", "Khoa học"],
    "Sách kỹ năng": ["Kỹ năng sống", "Sáng tạo", "Thể thao", "Âm nhạc"]
}

# ============ BOOKS DATA ============
# books_new = data_base().get_book()

def normalize_book(book_data):
    """Chuyển đổi dữ liệu sách từ Supabase thành format chuẩn"""
    try:
        return {
            'id': book_data.get('id'),
            'title': book_data.get('title', 'N/A'),
            'author': book_data.get('author', ''),
            'category': book_data.get('category', ''),
            'subcategory': book_data.get('subcategory', ''),
            'subject': book_data.get('subject', ''),
            'book_type': book_data.get('book_type', ''),
            'publisher': book_data.get('publisher', ''),
            'year': book_data.get('year', ''),
            'pages': book_data.get('pages', ''),
            'description': book_data.get('description', ''),
            'cover': book_data.get('cover', DEFAULT_BOOK_COVER),
            'pdf_file': book_data.get('pdf_file', ''),
            'views': int(book_data.get('views', 0)) if book_data.get('views') is not None else 0,
            'downloads': int(book_data.get('downloads', 0)) if book_data.get('downloads') is not None else 0,
            'rating': float(book_data.get('rating', 0)) if book_data.get('rating') is not None else 0,
            'available_copies': int(book_data.get('available_copies', 1)) if book_data.get('available_copies') is not None else 1,
            'total_copies': int(book_data.get('total_copies', 1)) if book_data.get('total_copies') is not None else 1,
            'borrowers': book_data.get('borrowers', []) if book_data.get('borrowers') is not None else []
        }
    except Exception as e:
        print(f"❌ Lỗi normalize book: {str(e)}")
        return None

def load_books_from_supabase():
    """Load books từ Supabase và normalize"""
    try:
        from static.py.database import db
        
        books_list = db().get_all_books_list()
        normalized_books = []
        
        for book in books_list:
            normalized = normalize_book(book)
            if normalized:
                normalized_books.append(normalized)
        
        print(f"✅ Loaded {len(normalized_books)} books từ Supabase")
        return normalized_books
    except Exception as e:
        print(f"❌ Lỗi load books: {str(e)}")
        return []
books_new = load_books_from_supabase()

if not books_new:
    print("⚠️ Không load được books từ Supabase, dùng fallback data")
    books_new = [
        {
            "id": 1, 
            "title": "Cậu bé đứng trên lưng chó",
            "category": "Truyện",
            "subcategory": "Truyện cổ tích",
            "book_type": "Truyện đọc",
            "author": "Tô Hoài",
            "publisher": "NXB Giáo Dục Việt Nam",
            "year": "2021",
            "pages": "120",
            "description": "Câu chuyện cổ tích lôi cuốn về chàng trai và con chó thần kỳ.",
            "cover": "TVcanhdieu1.jpg",
            "pdf_file": "https://dfvy4lc0t9aewcnl.public.blob.vercel-storage.com/books/tiengviet1-YIPU8Qcx072qRuo0j0xlMHDOuA0gLo.pdf",
            "views": 1250,
            "downloads": 85,
            "rating": 4.5,
            "available_copies": 3,
            "total_copies": 5,
            "borrowers": []
        }
    ]
books_popular = books_new[:3]
books_hot = sorted(books_new, key=lambda x: x['views'], reverse=True)[:6]
# ============ UTILITY FUNCTIONS ============


# ============ BOOKS DATA ============

def get_safe(obj, key, default=0, type_convert=int):
    """Lấy giá trị an toàn từ dict"""
    try:
        value = obj.get(key, default)
        if value is None:
            return default
        return type_convert(value)
    except (ValueError, TypeError):
        return default

def get_all_books():
    """Lấy tất cả books (safe)"""
    return books_new if books_new else []

def get_book_by_id(book_id):
    """Lấy sách theo ID (safe)"""
    try:
        all_books = get_all_books()
        return next((b for b in all_books if b.get('id') == book_id), None)
    except Exception as e:
        print(f"⚠️ Error get_book_by_id: {str(e)}")
        return None

def get_books_by_category(main_category, subcategory=None):
    """Lấy sách theo danh mục (safe)"""
    try:
        all_books = get_all_books()
        if subcategory:
            return [b for b in all_books 
                   if b.get('category') == main_category 
                   and b.get('subcategory') == subcategory]
        return [b for b in all_books if b.get('category') == main_category]
    except Exception as e:
        print(f"⚠️ Error get_books_by_category: {str(e)}")
        return []
@lru_cache(maxsize=256)
def image_exists(filename):
    """Kiểm tra ảnh có tồn tại (cache kết quả)"""
    if not filename:
        return False
    return os.path.isfile(os.path.join(IMAGES_FOLDER, filename))

@app.template_filter('cover')
def cover_filter(filename):
    """Filter: trả về tên ảnh nếu tồn tại, không thì dùng ảnh mặc định"""
    if image_exists(filename):
        return filename
    return DEFAULT_BOOK_COVER

# Inject vào template
@app.context_processor
def inject_defaults():
    return {
        'DEFAULT_COVER': DEFAULT_BOOK_COVER,
        'image_exists': image_exists
    }
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_card_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_globals():
    return {
        'int': int, 
        'session': session, 
        'datetime': datetime,
        'categories': CATEGORIES
    }

# ============ AUTH ROUTES ============
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        card_id = request.form.get('card_id')
        password = request.form.get('password')
        
        if card_id in users_db and users_db[card_id]['password'] == password:
            session['user_card_id'] = card_id
            session['user_name'] = users_db[card_id]['name']
            session['user_email'] = users_db[card_id]['email']
            next_page = request.args.get('next', '/')
            return redirect(next_page)
        else:
            return render_template('login.html', error='Mã thẻ hoặc mật khẩu không đúng')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ============ MAIN ROUTES ============

@app.route('/')
def home():
    sort = request.args.get('sort', 'new')
    
    try:
        if sort == 'new':
            books_display = sorted(get_all_books(), 
                                  key=lambda x: x.get('id', 0), reverse=True)[:6]
        elif sort == 'popular':
            books_display = sorted(get_all_books(), 
                                  key=lambda x: get_safe(x, 'downloads', 0), reverse=True)[:6]
        elif sort == 'views':
            books_display = sorted(get_all_books(), 
                                  key=lambda x: get_safe(x, 'views', 0), reverse=True)[:6]
        else:
            books_display = books_hot
        
        return render_template('index.html', 
                             books_new=get_all_books()[:6],
                             books_popular=books_popular,
                             books_hot=books_hot,
                             categories=CATEGORIES)
    except Exception as e:
        print(f"❌ Error home: {str(e)}")
        return render_template('index.html', 
                             books_new=[],
                             books_popular=[],
                             books_hot=[],
                             categories=CATEGORIES)
@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return render_template('404.html', message='Sách không tìm thấy'), 404
    
    is_favorite = False
    
    if 'user_card_id' in session:
        card_id = session['user_card_id']
        user_info = users_db.get(card_id, {})
        is_favorite = book_id in user_info.get('favorite_books', [])
    
    return render_template('book_detail.html', 
                         book=book, 
                         is_favorite=is_favorite)

@app.route('/category/<category>')
def category_main(category):
    try:
        # Decode URL encoding
        category = unquote(category)
        
        if category not in CATEGORIES:
            return render_template('error.html', 
                                 error='Danh mục không tìm thấy'), 404
        
        books = get_books_by_category(category)
        subcategories = CATEGORIES[category]
        
        return render_template('category_main.html', 
                             main_category=category,
                             subcategories=subcategories,
                             books=books,
                             categories=CATEGORIES)
    except Exception as e:
        print(f"Error in category_main: {str(e)}")
        return render_template('error.html', 
                             error=f'Lỗi: {str(e)}'), 500


@app.route('/category/<main_category>/<subcategory>')
def category_detail(main_category, subcategory):
    try:
        # Decode URL encoding
        main_category = unquote(main_category)
        subcategory = unquote(subcategory)
        
        if main_category not in CATEGORIES or subcategory not in CATEGORIES[main_category]:
            return render_template('error.html', 
                                 error='Danh mục không tìm thấy'), 404
        
        books = get_books_by_category(main_category, subcategory)
        
        return render_template('category_detail.html', 
                             main_category=main_category,
                             subcategory=subcategory,
                             books=books,
                             categories=CATEGORIES)
    except Exception as e:
        print(f"Error in category_detail: {str(e)}")
        return render_template('error.html', 
                             error=f'Lỗi: {str(e)}'), 500


@app.route('/search')
def search():
    try:
        query = request.args.get('q', '').strip()
        category_filter = request.args.get('category', '')
        
        all_books = get_all_books()
        results = []
        
        if query:
            results = [b for b in all_books 
                      if query.lower() in b.get('title', '').lower() 
                      or query.lower() in b.get('author', '').lower()]
        
        if category_filter and category_filter != 'all':
            results = [b for b in results if b.get('category') == category_filter]
        
        return render_template('search.html', 
                             search_results=results,
                             search_query=query,
                             categories=CATEGORIES)
    except Exception as e:
        print(f"Error in search: {str(e)}")
        return render_template('error.html', 
                             error=f'Lỗi: {str(e)}'), 500

# ============ ERROR HANDLERS ============
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', 
                         message='Trang không tìm thấy'), 404

@app.errorhandler(500)
def server_error(error):
    print(f"Server Error: {str(error)}")
    return render_template('error.html', 
                         error=str(error)), 500

@app.errorhandler(Exception)
def handle_exception(e):
    print(f"Exception: {str(e)}")
    return render_template('error.html', 
                         error=str(e)), 500

# ...existing code...

@app.route('/profile')
@login_required
def profile():
    card_id = session['user_card_id']
    user_info = users_db.get(card_id, {})
    
    favorite_books = []
    for book_id in user_info.get('favorite_books', []):
        book = get_book_by_id(book_id)
        if book:
            favorite_books.append(book)
    
    return render_template('profile.html', 
                         user_info=user_info, 
                         card_id=card_id,
                         favorite_books=favorite_books,
                         favorite_books_count=len(favorite_books))

# ...existing code...
@app.route('/favorites')
@login_required
def favorites():
    card_id = session['user_card_id']
    user_info = users_db[card_id]
    
    favorite_books = []
    for book_id in user_info.get('favorite_books', []):
        book = get_book_by_id(book_id)
        if book:
            favorite_books.append(book)
    
    return render_template('favorites.html', 
                         favorite_books=favorite_books,
                         favorite_books_count=len(favorite_books),
                         categories=CATEGORIES)

# ============ API ROUTES ============
@app.route('/api/favorite/<int:book_id>', methods=['POST'])
def toggle_favorite(book_id):
    if 'user_card_id' not in session:
        return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
    
    if not get_book_by_id(book_id):
        return jsonify({'success': False, 'message': 'Sách không tồn tại'}), 404
    
    card_id = session['user_card_id']
    user_info = users_db[card_id]
    
    if book_id in user_info['favorite_books']:
        user_info['favorite_books'].remove(book_id)
        is_favorite = False
    else:
        user_info['favorite_books'].append(book_id)
        is_favorite = True
    
    return jsonify({
        'success': True,
        'is_favorite': is_favorite,
        'message': 'Đã cập nhật'
    })

# ============ FILE ROUTES ============
@app.route('/read/<int:book_id>')
@login_required
def read_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return render_template('404.html', message='Sách không tìm thấy'), 404
    
    return render_template('book_reader.html', book=book)

# ...existing code...

@app.route('/download/<int:book_id>')
@login_required
def download_book(book_id):
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'success': False, 'message': 'Sách không tìm thấy'}), 404
    
    pdf_file = book.get('pdf_file', '')
    
    # Nếu là link URL - redirect
    if pdf_file.startswith('http'):
        book['downloads'] += 1
        return redirect(pdf_file)
    
    # Nếu là file local
    if pdf_file:
        file_path = os.path.join(UPLOAD_FOLDER, 'textbook', pdf_file.split('/')[-1])
        if os.path.exists(file_path):
            book['downloads'] += 1
            return send_from_directory(
                os.path.dirname(file_path),
                os.path.basename(file_path),
                as_attachment=True,
                download_name=f"{book['title']}.pdf"
            )
    
    return jsonify({'success': False, 'message': 'File không tìm thấy'}), 404

# ...existing code...
@app.route('/pdf/<path:filename>')
@login_required
def serve_pdf(filename):
    file_path = os.path.join(UPLOAD_FOLDER, 'textbook', filename)
    if not os.path.exists(file_path):
        return render_template('404.html', message='File không tìm thấy'), 404
    
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'textbook'), filename)
@app.route('/borrowed-books')
@login_required
def borrowed_books():
    card_id = session['user_card_id']
    user_info = users_db[card_id]
    
    borrowed = user_info.get('borrowed_books', [])
    
    return render_template('borrowed_books.html', 
                         borrowed_books=borrowed,
                         card_id=card_id)
# # ============ ERROR HANDLERS ============
# @app.errorhandler(404)
# def not_found(error):
#     return render_template('404.html', message='Trang không tìm thấy'), 404

# @app.errorhandler(500)
# def server_error(error):
#     return render_template('500.html', message='Lỗi server'), 500




# ____________________________________admin__________________________________


# ============ AUTH DECORATOR ============
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_user' not in session:
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ============ ADMIN ROUTES ============
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['admin_user'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Tên đăng nhập hoặc mật khẩu không đúng')
    
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_user', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    total_books = len(books_new)
    total_users = len(users_db)
    total_borrowed = sum(len(u.get('borrowed_books', [])) for u in users_db.values())
    
    stats = {
        'total_books': total_books,
        'total_users': total_users,
        'total_borrowed': total_borrowed,
        'categories': len(CATEGORIES)
    }
    
    return render_template('admin_dashboard.html', stats=stats, categories=CATEGORIES)

# ============ ADMIN - MANAGE CATEGORIES ============
@app.route('/admin/categories')
@admin_required
def admin_categories():
    return render_template('admin_categories.html', categories=CATEGORIES)

@app.route('/admin/api/add-category', methods=['POST'])
@admin_required
def admin_add_category():
    data = request.get_json()
    category_name = data.get('category_name', '').strip()
    
    if not category_name:
        return jsonify({'success': False, 'message': 'Tên danh mục không được trống'}), 400
    
    if category_name in CATEGORIES:
        return jsonify({'success': False, 'message': 'Danh mục đã tồn tại'}), 400
    
    CATEGORIES[category_name] = []
    
    return jsonify({
        'success': True,
        'message': 'Danh mục đã được thêm',
        'categories': CATEGORIES
    })

@app.route('/admin/api/delete-category/<category_name>', methods=['POST'])
@admin_required
def admin_delete_category(category_name):
    if category_name not in CATEGORIES:
        return jsonify({'success': False, 'message': 'Danh mục không tồn tại'}), 404
    
    # Kiểm tra có sách trong danh mục không
    books_in_category = [b for b in books_new if b['category'] == category_name]
    if books_in_category:
        return jsonify({'success': False, 'message': f'Danh mục này có {len(books_in_category)} cuốn sách, không thể xóa'}), 400
    
    del CATEGORIES[category_name]
    
    return jsonify({
        'success': True,
        'message': 'Danh mục đã được xóa',
        'categories': CATEGORIES
    })

# ============ ADMIN - MANAGE BOOKS ============
@app.route('/admin/books')
@admin_required
def admin_books():
    return render_template('admin_books.html', books=books_new, categories=CATEGORIES)

@app.route('/admin/api/books')
@admin_required
def admin_get_books():
    return jsonify(books_new)

@app.route('/admin/api/add-book', methods=['POST'])
@admin_required
def admin_add_book():
    data = request.get_json()
    
    # Tìm ID lớn nhất
    max_id = max([b['id'] for b in books_new]) if books_new else 0
    new_id = max_id + 1
    
    new_book = {
        'id': new_id,
        'title': data.get('title', ''),
        'category': data.get('category', ''),
        'subcategory': data.get('subcategory', ''),
        'subject': data.get('subject', ''),
        'book_type': data.get('book_type', ''),
        'author': data.get('author', ''),
        'publisher': data.get('publisher', ''),
        'year': data.get('year', ''),
        'pages': data.get('pages', ''),
        'description': data.get('description', ''),
        'cover': data.get('cover', DEFAULT_BOOK_COVER),
        'pdf_file': data.get('pdf_file', ''),
        'views': 0,
        'downloads': 0,
        'rating': 0,
        'available_copies': int(data.get('available_copies', 1)),
        'total_copies': int(data.get('total_copies', 1)),
        'borrowers': []
    }
    
    books_new.append(new_book)
    
    return jsonify({
        'success': True,
        'message': 'Sách đã được thêm',
        'book': new_book
    })

@app.route('/admin/api/edit-book/<int:book_id>', methods=['POST'])
@admin_required
def admin_edit_book(book_id):
    data = request.get_json()
    book = get_book_by_id(book_id)
    
    if not book:
        return jsonify({'success': False, 'message': 'Sách không tồn tại'}), 404
    
    # Cập nhật thông tin
    book['title'] = data.get('title', book['title'])
    book['author'] = data.get('author', book['author'])
    book['publisher'] = data.get('publisher', book['publisher'])
    book['category'] = data.get('category', book['category'])
    book['subcategory'] = data.get('subcategory', book['subcategory'])
    book['subject'] = data.get('subject', book.get('subject', ''))
    book['description'] = data.get('description', book['description'])
    book['pages'] = data.get('pages', book['pages'])
    book['year'] = data.get('year', book['year'])
    book['available_copies'] = int(data.get('available_copies', book['available_copies']))
    book['total_copies'] = int(data.get('total_copies', book['total_copies']))
    
    return jsonify({
        'success': True,
        'message': 'Sách đã được cập nhật',
        'book': book
    })

@app.route('/admin/api/delete-book/<int:book_id>', methods=['POST'])
@admin_required
def admin_delete_book(book_id):
    global books_new
    
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'success': False, 'message': 'Sách không tồn tại'}), 404
    
    books_new = [b for b in books_new if b['id'] != book_id]
    
    return jsonify({
        'success': True,
        'message': 'Sách đã được xóa'
    })

# ============ ADMIN - MANAGE USERS ============
@app.route('/admin/users')
@admin_required
def admin_users():
    return render_template('admin_users.html', users=users_db)

@app.route('/admin/api/users')
@admin_required
def admin_get_users():
    users_list = []
    for card_id, user_info in users_db.items():
        users_list.append({
            'card_id': card_id,
            'name': user_info['name'],
            'email': user_info['email'],
            'phone': user_info['phone'],
            'borrowed_count': len(user_info.get('borrowed_books', [])),
            'favorite_count': len(user_info.get('favorite_books', []))
        })
    
    return jsonify(users_list)

@app.route('/admin/api/user/<card_id>')
@admin_required
def admin_get_user(card_id):
    if card_id not in users_db:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
    
    user = users_db[card_id]
    return jsonify({
        'card_id': card_id,
        'name': user['name'],
        'email': user['email'],
        'phone': user['phone'],
        'borrowed_books': user.get('borrowed_books', []),
        'favorite_books': user.get('favorite_books', []),
        'borrow_limit': user.get('borrow_limit', 5)
    })

@app.route('/admin/api/add-user', methods=['POST'])
@admin_required
def admin_add_user():
    data = request.get_json()
    card_id = data.get('card_id', '').strip()
    
    if not card_id:
        return jsonify({'success': False, 'message': 'Mã thẻ không được trống'}), 400
    
    if card_id in users_db:
        return jsonify({'success': False, 'message': 'Mã thẻ đã tồn tại'}), 400
    
    new_user = {
        'password': data.get('password', 'password123'),
        'name': data.get('name', ''),
        'email': data.get('email', ''),
        'phone': data.get('phone', ''),
        'borrowed_books': [],
        'favorite_books': [],
        'borrow_limit': 5
    }
    
    users_db[card_id] = new_user
    
    return jsonify({
        'success': True,
        'message': 'Người dùng đã được thêm'
    })

@app.route('/admin/api/edit-user/<card_id>', methods=['POST'])
@admin_required
def admin_edit_user(card_id):
    if card_id not in users_db:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
    
    data = request.get_json()
    user = users_db[card_id]
    
    user['name'] = data.get('name', user['name'])
    user['email'] = data.get('email', user['email'])
    user['phone'] = data.get('phone', user['phone'])
    user['borrow_limit'] = int(data.get('borrow_limit', user.get('borrow_limit', 5)))
    
    return jsonify({
        'success': True,
        'message': 'Người dùng đã được cập nhật'
    })

@app.route('/admin/api/delete-user/<card_id>', methods=['POST'])
@admin_required
def admin_delete_user(card_id):
    if card_id not in users_db:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
    
    del users_db[card_id]
    
    return jsonify({
        'success': True,
        'message': 'Người dùng đã được xóa'
    })

# ============ ADMIN - MANAGE BORROWED BOOKS ============
@app.route('/admin/borrowed')
@admin_required
def admin_borrowed():
    borrowed_list = []
    
    for card_id, user_info in users_db.items():
        for book in user_info.get('borrowed_books', []):
            borrowed_list.append({
                'card_id': card_id,
                'user_name': user_info['name'],
                'book_id': book['book_id'],
                'book_title': book['title'],
                'borrow_date': book['borrow_date'],
                'due_date': book['due_date'],
                'status': book['status']
            })
    
    return render_template('admin_borrowed.html', borrowed_list=borrowed_list)

@app.route('/admin/api/add-borrow', methods=['POST'])
@admin_required
def admin_add_borrow():
    data = request.get_json()
    card_id = data.get('card_id')
    book_id = int(data.get('book_id'))
    
    if card_id not in users_db:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
    
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({'success': False, 'message': 'Sách không tồn tại'}), 404
    
    user = users_db[card_id]
    
    # Kiểm tra đã mượn chưa
    for b in user.get('borrowed_books', []):
        if b.get('book_id') == book_id:
            return jsonify({'success': False, 'message': 'Người dùng đã mượn sách này'}), 400
    
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    
    new_borrow = {
        'book_id': book_id,
        'title': book.get('title', 'N/A'),
        'borrow_date': borrow_date,
        'due_date': due_date,
        'status': 'đang mượn'
    }
    
    if 'borrowed_books' not in user:
        user['borrowed_books'] = []
    
    user['borrowed_books'].append(new_borrow)
    
    return jsonify({
        'success': True,
        'message': 'Sách đã được cấp cho người dùng'
    })

@app.route('/admin/api/return-book', methods=['POST'])
@admin_required
def admin_return_book():
    data = request.get_json()
    card_id = data.get('card_id')
    book_id = int(data.get('book_id'))
    
    if card_id not in users_db:
        return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
    
    user = users_db[card_id]
    
    # Tìm sách đang mượn
    for i, book in enumerate(user.get('borrowed_books', [])):
        if book['book_id'] == book_id:
            user['borrowed_books'].pop(i)
            return jsonify({
                'success': True,
                'message': 'Sách đã được trả'
            })
    
    return jsonify({'success': False, 'message': 'Không tìm thấy sách'}), 404

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============ IMPORT DATA ROUTES ============
@app.route('/admin/import-students', methods=['POST'])
@admin_required
def admin_import_students():
    """Import học sinh từ file TXT"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file được tải lên'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Chỉ chấp nhận file .txt hoặc .csv'}), 400
    
    try:
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        imported_count = 0
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Bỏ qua dòng trống và comment
                continue
            
            parts = [p.strip() for p in line.split('|')]
            
            if len(parts) < 4:
                errors.append(f"Dòng {line_num}: Thiếu dữ liệu (cần: Mã thẻ|Tên|Email|SĐT)")
                continue
            
            card_id, name, email, phone = parts[0], parts[1], parts[2], parts[3]
            password = parts[4] if len(parts) > 4 else 'password123'
            
            # Kiểm tra mã thẻ đã tồn tại
            if card_id in users_db:
                errors.append(f"Dòng {line_num}: Mã thẻ '{card_id}' đã tồn tại")
                continue
            
            # Thêm học sinh
            users_db[card_id] = {
                'password': password,
                'name': name,
                'email': email,
                'phone': phone,
                'borrowed_books': [],
                'favorite_books': [],
                'borrow_limit': 5
            }
            
            imported_count += 1
        
        message = f'Đã import {imported_count} học sinh'
        if errors:
            message += f'\n⚠️ Lỗi: {len(errors)} dòng'
        
        return jsonify({
            'success': True,
            'message': message,
            'imported': imported_count,
            'errors': errors[:10]  # Chỉ trả 10 lỗi đầu tiên
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/admin/import-books', methods=['POST'])
@admin_required
def admin_import_books():
    """Import sách từ file TXT"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'Không có file được tải lên'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': 'Chưa chọn file'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'Chỉ chấp nhận file .txt hoặc .csv'}), 400
    
    try:
        content = file.read().decode('utf-8')
        lines = content.strip().split('\n')
        
        imported_count = 0
        errors = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = [p.strip() for p in line.split('|')]
            
            # Tối thiểu: Tên|Tác giả|Danh mục|Lớp
            if len(parts) < 4:
                errors.append(f"Dòng {line_num}: Thiếu dữ liệu (cần: Tên|Tác giả|Danh mục|Lớp)")
                continue
            
            title, author, category, subcategory = parts[0], parts[1], parts[2], parts[3]
            
            # Kiểm tra danh mục tồn tại
            if category not in CATEGORIES:
                errors.append(f"Dòng {line_num}: Danh mục '{category}' không tồn tại")
                continue
            
            # Tìm ID lớn nhất
            max_id = max([b['id'] for b in books_new]) if books_new else 0
            new_id = max_id + 1
            
            # Tạo sách mới
            new_book = {
                'id': new_id,
                'title': title,
                'author': author,
                'category': category,
                'subcategory': subcategory,
                'subject': parts[4] if len(parts) > 4 else '',
                'publisher': parts[5] if len(parts) > 5 else '',
                'year': parts[6] if len(parts) > 6 else '',
                'pages': parts[7] if len(parts) > 7 else '',
                'description': parts[8] if len(parts) > 8 else '',
                'cover': DEFAULT_BOOK_COVER,
                'pdf_file': '',
                'views': 0,
                'downloads': 0,
                'rating': 0,
                'available_copies': int(parts[9]) if len(parts) > 9 else 1,
                'total_copies': int(parts[10]) if len(parts) > 10 else 1,
                'borrowers': []
            }
            
            books_new.append(new_book)
            imported_count += 1
        
        message = f'Đã import {imported_count} cuốn sách'
        if errors:
            message += f'\n⚠️ Lỗi: {len(errors)} dòng'
        
        return jsonify({
            'success': True,
            'message': message,
            'imported': imported_count,
            'errors': errors[:10]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Lỗi: {str(e)}'}), 500

@app.route('/admin/download-template/<template_type>')
@admin_required
def download_template(template_type):
    """Tải template file mẫu"""
    if template_type == 'students':
        content = """# Mẫu import học sinh - Các trường bắt buộc: Mã thẻ|Tên|Email|SĐT
# Định dạng: Mã thẻ|Tên|Email|SĐT|Mật khẩu (tuỳ chọn)
# Ví dụ:
TV001|Nguyễn Văn A|vana@example.com|0123456789|password123
TV002|Trần Thị B|thib@example.com|0987654321
TV003|Lê Văn C|vanc@example.com|0111111111"""
    
    elif template_type == 'books':
        content = """# Mẫu import sách - Các trường bắt buộc: Tên|Tác giả|Danh mục|Lớp
# Định dạng: Tên|Tác giả|Danh mục|Lớp|Môn học|NXB|Năm|Trang|Mô tả|Còn|Tổng
# Ví dụ:
Tiếng Việt 1|Bộ GD&ĐT|Sách giáo khoa|Lớp 1|Tiếng Việt|NXB Giáo dục|2023|100|Sách học|5|5
Toán 1|Bộ GD&ĐT|Sách giáo khoa|Lớp 1|Toán|NXB Giáo dục|2023|80|Sách học|3|3"""
    
    else:
        return jsonify({'success': False, 'message': 'Template không hợp lệ'}), 400
    
    from io import BytesIO
    return send_file(
        BytesIO(content.encode('utf-8')),
        mimetype='text/plain',
        as_attachment=True,
        download_name=f'template_{template_type}.txt'
    )
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)