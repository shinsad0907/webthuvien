# import requests
# import os

# # Token của bạn
# BLOB_READ_WRITE_TOKEN = "vercel_blob_rw_DFVY4lc0T9aEwcNL_SoKkXhxMeVhefRAcAV1rjnJGQ6zkTO"

# def upload_to_vercel_blob(file_path, blob_path, access='public'):
#     """
#     Upload file lên Vercel Blob
    
#     Args:
#         file_path: Đường dẫn file local cần upload
#         blob_path: Đường dẫn trên Vercel Blob (ví dụ: 'articles/blob.txt')
#         access: 'public' hoặc 'private'
    
#     Returns:
#         dict: Response từ Vercel Blob API
#     """
    
#     # API endpoint
#     url = f"https://blob.vercel-storage.com/{blob_path}"
    
#     # Headers
#     headers = {
#         "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
#         "x-api-version": "7"
#     }
    
#     # Đọc file
#     with open(file_path, 'rb') as f:
#         file_content = f.read()
    
#     # Query parameters
#     params = {
#         "access": access
#     }
    
#     # Upload file
#     response = requests.put(url, headers=headers, params=params, data=file_content)
    
#     if response.status_code == 200:
#         result = response.json()
#         print(f"✅ Upload thành công!")
#         print(f"URL: {result.get('url')}")
#         return result
#     else:
#         print(f"❌ Upload thất bại: {response.status_code}")
#         print(f"Error: {response.text}")
#         return None


# def upload_text_to_vercel_blob(text_content, blob_path, access='public'):
#     """
#     Upload text trực tiếp lên Vercel Blob (không cần file)
    
#     Args:
#         text_content: Nội dung text cần upload
#         blob_path: Đường dẫn trên Vercel Blob
#         access: 'public' hoặc 'private'
    
#     Returns:
#         dict: Response từ Vercel Blob API
#     """
    
#     url = f"https://blob.vercel-storage.com/{blob_path}"
    
#     headers = {
#         "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
#         "x-api-version": "7"
#     }
    
#     params = {
#         "access": access
#     }
    
#     response = requests.put(url, headers=headers, params=params, data=text_content.encode('utf-8'))
    
#     if response.status_code == 200:
#         result = response.json()
#         print(f"✅ Upload thành công!")
#         print(f"URL: {result.get('url')}")
#         return result
#     else:
#         print(f"❌ Upload thất bại: {response.status_code}")
#         print(f"Error: {response.text}")
#         return None


# # Ví dụ sử dụng:

# # 1. Upload text trực tiếp (giống ví dụ JavaScript của bạn)
# print("=== Upload text ===")
# upload_text_to_vercel_blob('Hello World!', 'articles/blob.txt')

# # 2. Upload file từ máy tính
# print("\n=== Upload file ===")
# # upload_to_vercel_blob('path/to/your/file.txt', 'articles/myfile.txt')

# # 3. Upload hình ảnh
# # upload_to_vercel_blob('image.jpg', 'images/photo.jpg')

text = r'C:\Users\pc\Desktop\shin\manager_web\tiengviet1.pdf'
print(text.split('.')[0].split('\\')[-1])