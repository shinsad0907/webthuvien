from flask import Flask, render_template, request, url_for, send_from_directory, session, redirect, jsonify
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename
from functools import wraps, lru_cache

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'
DEFAULT_BOOK_COVER = 'fs_book_cover-5f4eddfb.png'
IMAGES_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'images')
ALLOWED_EXTENSIONS = {'txt', 'csv'}
UPLOAD_FOLDER = r'C:\Users\pc\Desktop\shin\webdocsach\data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ============ DATABASE ============
ADMIN_CREDENTIALS = {
    'admin': 'admin',  # Thay đổi mật khẩu này!
    'admin2': 'shinsad'
}
users_db = {
    'TV001': {
        'password': 'password123',
        'name': 'Nguyễn Văn A',
        'email': 'user1@example.com',
        'phone': '0123456789',
        'borrowed_books': [
            {
                'book_id': 1,
                'title': 'Cậu bé đứng trên lưng chó',
                'borrow_date': '2024-11-14',
                'due_date': '2024-11-28',
                'status': 'đang mượn'
            }
        ],
        'favorite_books': [1, 2],
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
        "pdf_file": "https://2e9gpvwy1fi1gblk.public.blob.vercel-storage.com/C%E1%BA%ADu%20b%C3%A9%20%C4%91%E1%BB%A9ng%20tr%C3%AAn%20l%C6%B0ng%20ch%C3%B3.pdf",
        "views": 1250,
        "downloads": 85,
        "rating": 4.5,
        "available_copies": 3,
        "total_copies": 5,
        "borrowers": []
    },
    {
        "id": 2, 
        "title": "Sự tích Hạ Long",
        "category": "Truyện",
        "subcategory": "Truyện cổ tích",
        "book_type": "Sách giáo viên",
        "author": "Dân gian",
        "publisher": "NXB Thanh Niên",
        "year": "2020",
        "pages": "100",
        "description": "Truyện cổ tích nổi tiếng về Hạ Long Bay.",
        "cover": "book2.jpg",
        "pdf_file": "textbook/book2.pdf",
        "views": 850,
        "downloads": 45,
        "rating": 4.2,
        "available_copies": 2,
        "total_copies": 4,
        "borrowers": []
    },
    {
        "id": 3, 
        "title": "Tấm Cám",
        "category": "Truyện",
        "subcategory": "Truyện cổ tích",
        "book_type": "Sách giáo khóa",
        "author": "Dân gian",
        "publisher": "NXB Thanh Niên",
        "year": "2020",
        "pages": "95",
        "description": "Truyện cổ tích Tấm Cám - câu chuyện về lòng tốt và công lý.",
        "cover": "book3.jpg",
        "pdf_file": "textbook/book3.pdf",
        "views": 920,
        "downloads": 56,
        "rating": 4.3,
        "available_copies": 4,
        "total_copies": 5,
        "borrowers": []
    },
    {
        "id": 4, 
        "title": "Thạch Sanh - Lê Phương",
        "category": "Truyện",
        "subcategory": "Truyện cổ tích",
        "book_type": "Truyện đọc",
        "author": "Dân gian",
        "publisher": "NXB Thanh Niên",
        "year": "2020",
        "pages": "110",
        "description": "Chuyện tình lãng mạn của Thạch Sanh và Lê Phương.",
        "cover": "book4.jpg",
        "pdf_file": "textbook/book4.pdf",
        "views": 740,
        "downloads": 38,
        "rating": 4.1,
        "available_copies": 5,
        "total_copies": 5,
        "borrowers": []
    },
    {
        "id": 5, 
        "title": "Truyện Kiều",
        "category": "Sách tham khảo",
        "subcategory": "Tiếng Việt",
        "book_type": "Sách giáo khóa",
        "author": "Nguyễn Du",
        "publisher": "NXB Văn học",
        "year": "2019",
        "pages": "200",
        "description": "Bộ truyện Kiều nổi tiếng nhất của Nguyễn Du.",
        "cover": "book5.jpg",
        "pdf_file": "textbook/book5.pdf",
        "views": 1100,
        "downloads": 72,
        "rating": 4.4,
        "available_copies": 3,
        "total_copies": 5,
        "borrowers": []
    },
    {
        "id": 6, 
        "title": "Kỳ tích hai mươi năm",
        "category": "Truyện",
        "subcategory": "Truyện hiện đại",
        "book_type": "Truyện đọc",
        "author": "Jules Verne",
        "publisher": "NXB Trẻ",
        "year": "2021",
        "pages": "250",
        "description": "Cuộc phiêu lưu tứ tế vòng quanh thế giới.",
        "cover": "book6.jpg",
        "pdf_file": "textbook/book6.pdf",
        "views": 980,
        "downloads": 61,
        "rating": 4.2,
        "available_copies": 2,
        "total_copies": 4,
        "borrowers": []
    },
    {
        "id": 7, 
        "title": "Toán lớp 1",
        "category": "Sách giáo khóa",
        "subcategory": "Lớp 1",
        "book_type": "Sách giáo khóa",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "150",
        "description": "Sách giáo khóa toán lớp 1 theo chương trình mới.",
        "cover": "book7.jpg",
        "pdf_file": "textbook/book7.pdf",
        "views": 650,
        "downloads": 42,
        "rating": 4.0,
        "available_copies": 5,
        "total_copies": 8,
        "borrowers": []
    },
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
        "cover": "book1.jpg",
        "pdf_file": "textbook/book1.pdf",
        "views": 1250,
        "downloads": 85,
        "rating": 4.5,
        "available_copies": 3,
        "total_copies": 5,
        "borrowers": []
    },
    
    # ===== SÁCH GIÁO KHÓA LỚP 1 =====
    {
        "id": 7, 
        "title": "Toán Kết Nối Tri Thức Lớp 1",
        "category": "Sách giáo khóa",
        "subcategory": "Lớp 1",
        "subject": "Toán",
        "book_type": "Sách giáo khóa",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "150",
        "description": "Sách giáo khóa toán lớp 1 theo chương trình Kết Nối Tri Thức.",
        "cover": "book7.jpg",
        "pdf_file": "textbook/toan_l1.pdf",
        "views": 650,
        "downloads": 42,
        "rating": 4.0,
        "available_copies": 5,
        "total_copies": 8,
        "borrowers": []
    },
    {
        "id": 8, 
        "title": "Tiếng Việt Kết Nối Tri Thức Lớp 1",
        "category": "Sách giáo khóa",
        "subcategory": "Lớp 1",
        "subject": "Tiếng Việt",
        "book_type": "Sách giáo khóa",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "160",
        "description": "Sách giáo khóa tiếng Việt lớp 1 theo chương trình Kết Nối Tri Thức.",
        "cover": "book8.jpg",
        "pdf_file": "textbook/tiengviet_l1.pdf",
        "views": 580,
        "downloads": 38,
        "rating": 4.1,
        "available_copies": 4,
        "total_copies": 7,
        "borrowers": []
    },
    {
        "id": 9, 
        "title": "Tự Nhiên Xã Hội Lớp 1",
        "category": "Sách giáo khóa",
        "subcategory": "Lớp 1",
        "subject": "Tự Nhiên Xã Hội",
        "book_type": "Sách giáo khóa",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "140",
        "description": "Sách giáo khóa tự nhiên xã hội lớp 1.",
        "cover": "book9.jpg",
        "pdf_file": "textbook/tnxh_l1.pdf",
        "views": 420,
        "downloads": 25,
        "rating": 3.9,
        "available_copies": 6,
        "total_copies": 8,
        "borrowers": []
    },
    
    # ===== SÁCH GIÁO KHÓA LỚP 2 =====
    {
        "id": 10, 
        "title": "Toán Kết Nối Tri Thức Lớp 2",
        "category": "Sách giáo khóa",
        "subcategory": "Lớp 2",
        "subject": "Toán",
        "book_type": "Sách giáo khóa",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "170",
        "description": "Sách giáo khóa toán lớp 2 theo chương trình Kết Nối Tri Thức.",
        "cover": "book10.jpg",
        "pdf_file": "textbook/toan_l2.pdf",
        "views": 720,
        "downloads": 50,
        "rating": 4.2,
        "available_copies": 5,
        "total_copies": 8,
        "borrowers": []
    },
    {
        "id": 11, 
        "title": "Tiếng Việt Kết Nối Tri Thức Lớp 2",
        "category": "Sách giáo khóa",
        "subcategory": "Lớp 2",
        "subject": "Tiếng Việt",
        "book_type": "Sách giáo khóa",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "180",
        "description": "Sách giáo khóa tiếng Việt lớp 2.",
        "cover": "book11.jpg",
        "pdf_file": "textbook/tiengviet_l2.pdf",
        "views": 650,
        "downloads": 45,
        "rating": 4.0,
        "available_copies": 4,
        "total_copies": 7,
        "borrowers": []
    },
    
    # ===== SÁCH GIÁO VIÊN LỚP 1 =====
    {
        "id": 20, 
        "title": "Hướng Dẫn Giảng Dạy Toán Lớp 1",
        "category": "Sách giáo viên",
        "subcategory": "Lớp 1",
        "subject": "Toán",
        "book_type": "Sách giáo viên",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "200",
        "description": "Sách hướng dẫn giảng dạy toán lớp 1 cho giáo viên.",
        "cover": "book20.jpg",
        "pdf_file": "textbook/huongdan_toan_l1.pdf",
        "views": 320,
        "downloads": 18,
        "rating": 4.3,
        "available_copies": 3,
        "total_copies": 5,
        "borrowers": []
    },
    {
        "id": 21, 
        "title": "Hướng Dẫn Giảng Dạy Tiếng Việt Lớp 1",
        "category": "Sách giáo viên",
        "subcategory": "Lớp 1",
        "subject": "Tiếng Việt",
        "book_type": "Sách giáo viên",
        "author": "Bộ Giáo Dục",
        "publisher": "NXB Giáo Dục Việt Nam",
        "year": "2024",
        "pages": "210",
        "description": "Sách hướng dẫn giảng dạy tiếng Việt lớp 1 cho giáo viên.",
        "cover": "book21.jpg",
        "pdf_file": "textbook/huongdan_tiengviet_l1.pdf",
        "views": 280,
        "downloads": 15,
        "rating": 4.2,
        "available_copies": 2,
        "total_copies": 4,
        "borrowers": []
    },
    
    # ===== TRUYỆN =====
    {
        "id": 2, 
        "title": "Sự tích Hạ Long",
        "category": "Truyện",
        "subcategory": "Truyện cổ tích",
        "book_type": "Truyện",
        "author": "Dân gian",
        "publisher": "NXB Thanh Niên",
        "year": "2020",
        "pages": "100",
        "description": "Truyện cổ tích nổi tiếng về Hạ Long Bay.",
        "cover": "book2.jpg",
        "pdf_file": "textbook/book2.pdf",
        "views": 850,
        "downloads": 45,
        "rating": 4.2,
        "available_copies": 2,
        "total_copies": 4,
        "borrowers": []
    },
]

books_popular = books_new[:3]
books_hot = sorted(books_new, key=lambda x: x['views'], reverse=True)[:6]
# ============ UTILITY FUNCTIONS ============
def get_all_books():
    return books_new

def get_book_by_id(book_id):
    all_books = get_all_books()
    return next((b for b in all_books if b['id'] == book_id), None)

def get_books_by_category(main_category, subcategory=None):
    all_books = get_all_books()
    if subcategory:
        return [b for b in all_books if b['category'] == main_category and b['subcategory'] == subcategory]
    return [b for b in all_books if b['category'] == main_category]
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
    
    if sort == 'new':
        books_display = sorted(books_new, key=lambda x: x['id'], reverse=True)[:6]
    elif sort == 'popular':
        books_display = sorted(books_new, key=lambda x: x['downloads'], reverse=True)[:6]
    elif sort == 'views':
        books_display = sorted(books_new, key=lambda x: x['views'], reverse=True)[:6]
    else:
        books_display = books_hot
    
    return render_template('index.html', 
                         books_new=books_new[:6],
                         books_popular=books_popular,
                         books_hot=books_hot,
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

@app.route('/category/<main_category>')
def category_main(main_category):
    if main_category not in CATEGORIES:
        return render_template('404.html', message='Danh mục không tìm thấy'), 404
    
    books = get_books_by_category(main_category)
    subcategories = CATEGORIES[main_category]
    
    return render_template('category_main.html', 
                         main_category=main_category,
                         subcategories=subcategories,
                         books=books,
                         categories=CATEGORIES)

@app.route('/category/<main_category>/<subcategory>')
def category_detail(main_category, subcategory):
    if main_category not in CATEGORIES or subcategory not in CATEGORIES[main_category]:
        return render_template('404.html', message='Danh mục không tìm thấy'), 404
    
    books = get_books_by_category(main_category, subcategory)
    
    return render_template('category_detail.html', 
                         main_category=main_category,
                         subcategory=subcategory,
                         books=books,
                         categories=CATEGORIES)

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '')
    
    all_books = get_all_books()
    results = []
    
    if query:
        results = [b for b in all_books if 
                  query.lower() in b['title'].lower() or 
                  query.lower() in b['author'].lower() or
                  query.lower() in b['description'].lower()]
    
    if category_filter and category_filter != 'all':
        results = [b for b in results if b['category'] == category_filter]
    
    return render_template('search.html', 
                         search_results=results,
                         search_query=query,
                         categories=CATEGORIES)

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
        if b['book_id'] == book_id:
            return jsonify({'success': False, 'message': 'Người dùng đã mượn sách này'}), 400
    
    borrow_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')
    
    new_borrow = {
        'book_id': book_id,
        'title': book['title'],
        'borrow_date': borrow_date,
        'due_date': due_date,
        'status': 'đang mượn'
    }
    
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