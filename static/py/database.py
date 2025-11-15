from supabase import create_client, Client
import json

class db:
    def __init__(self):
        self.SUPABASE_URL = "https://nnedehvvazuyxtrghjrd.supabase.co"
        self.SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5uZWRlaHZ2YXp1eXh0cmdoanJkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMxNDM0NzMsImV4cCI6MjA3ODcxOTQ3M30.cxmCbeHmAOFOhe-Cwh6gaXWRyEIeFCHl2qwtZBvghLQ"
        
        try:
            self.supabase: Client = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)
            print("✅ Kết nối Supabase thành công")
        except Exception as e:
            print(f"❌ Lỗi kết nối Supabase: {str(e)}")
            self.supabase = None
        
        self.users = []
        self.books = []
        self.borrowed = []
    
    def get_all_users_list(self):
        """Lấy users từ Supabase"""
        try:
            if not self.supabase:
                print("⚠️ Supabase chưa kết nối")
                return []
            
            response = self.supabase.table("users").select("*").execute()
            
            self.users = response.data if response.data else []
            print(f"✅ Lấy được {len(self.users)} users")
            return self.users
        except Exception as e:
            print(f"❌ Lỗi get_all_users_list: {str(e)}")
            return []
    
    def get_all_books_list(self):
        """Lấy books từ Supabase"""
        try:
            if not self.supabase:
                print("⚠️ Supabase chưa kết nối")
                return []
            
            response = self.supabase.table("books").select("*").execute()
            self.books = response.data if response.data else []
            
            print(f"✅ Lấy được {len(self.books)} books")
            return self.books
        except Exception as e:
            print(f"❌ Lỗi get_all_books_list: {str(e)}")
            return []
    
    def get_borrowed(self):
        """Lấy borrowed records"""
        try:
            if not self.supabase:
                print("⚠️ Supabase chưa kết nối")
                return []
            
            response = self.supabase.table("borrowed").select("*").execute()
            self.borrowed = response.data if response.data else []
            
            print(f"✅ Lấy được {len(self.borrowed)} borrowed records")
            return self.borrowed
        except Exception as e:
            print(f"❌ Lỗi get_borrowed: {str(e)}")
            return []
    
    def get_user_by_card_id(self, card_id):
        """Lấy user theo mã thẻ"""
        try:
            card_id = str(card_id).strip()
            for user in self.users:
                if str(user.get('card_id', '')).strip() == card_id:
                    return user
            return None
        except Exception as e:
            print(f"❌ Lỗi get_user_by_card_id: {str(e)}")
            return None
    
    def get_book_by_id(self, book_id):
        """Lấy book theo ID"""
        try:
            book_id = int(book_id)
            for book in self.books:
                if book.get('id') == book_id:
                    return book
            return None
        except Exception as e:
            print(f"❌ Lỗi get_book_by_id: {str(e)}")
            return None
    
    def search_books(self, query):
        """Tìm kiếm sách"""
        try:
            query = str(query).lower().strip()
            results = []
            
            for book in self.books:
                title = str(book.get('title', '')).lower()
                author = str(book.get('author', '')).lower()
                category = str(book.get('category', '')).lower()
                
                if query in title or query in author or query in category:
                    results.append(book)
            
            return results
        except Exception as e:
            print(f"❌ Lỗi search_books: {str(e)}")
            return []
    
    def get_data(self):
        """Lấy tất cả dữ liệu"""
        print("\n" + "="*80)
        print("📊 LOADING DATA FROM SUPABASE")
        print("="*80)
        
        self.get_all_users_list()
        self.get_all_books_list()
        self.get_borrowed()
        
        print("\n" + "="*80)
        print("📈 STATISTICS:")
        print(f"   👥 Users: {len(self.users)}")
        print(f"   📚 Books: {len(self.books)}")
        print(f"   📖 Borrowed: {len(self.borrowed)}")
        print("="*80 + "\n")
        
        return {
            "users": self.users,
            "books": self.books,
            "borrowed": self.borrowed,
            "categories": {
                "Sách giáo khóa": ["Lớp 1", "Lớp 2", "Lớp 3", "Lớp 4", "Lớp 5"],
                "Sách giáo viên": ["Lớp 1", "Lớp 2", "Lớp 3", "Lớp 4", "Lớp 5"],
                "Truyện": ["Truyện cổ tích", "Truyện hiện đại", "Truyện dạy bảo", "Truyện hành động"],
                "Sách tham khảo": ["Toán học", "Tiếng Việt", "Tiếng Anh", "Khoa học"],
                "Sách kỹ năng": ["Kỹ năng sống", "Sáng tạo", "Thể thao", "Âm nhạc"]
            }
        }


# ============ SINGLETON INSTANCE ============

# Khởi tạo instance
# db = DatabaseHandler()

# # Tự động load dữ liệu
# db.get_data()