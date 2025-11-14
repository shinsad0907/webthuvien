document.addEventListener('DOMContentLoaded', function() {
    const bookCards = document.querySelectorAll('.book-card');
    bookCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (e.target.closest('.favorite-btn')) return;
            const bookLink = this.querySelector('a[href*="/book/"]');
            if (bookLink) {
                window.location.href = bookLink.href;
            }
        });
    });

    const searchForm = document.querySelector('.search-bar form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const searchInput = this.querySelector('.search-input');
            const query = searchInput.value.trim();
            if (query) {
                window.location.href = `/search?q=${encodeURIComponent(query)}`;
            }
        });
    }
});

function toggleFavorite(bookId) {
    if (!checkLogin()) return;

    fetch(`/favorite/${bookId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const btn = event.target.closest('.favorite-btn');
            if (data.is_favorite) {
                btn.classList.add('active');
                btn.innerHTML = '<i class="fas fa-heart"></i>';
                showNotification('Đã thêm vào yêu thích', 'success');
            } else {
                btn.classList.remove('active');
                btn.innerHTML = '<i class="far fa-heart"></i>';
                showNotification('Đã xóa khỏi yêu thích', 'success');
            }
        }
    })
    .catch(err => {
        console.error('Lỗi:', err);
        showNotification('Lỗi xảy ra', 'error');
    });
}

function borrowBook(bookId) {
    if (!checkLogin()) return;

    fetch(`/borrow/${bookId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            setTimeout(() => {
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    location.reload();
                }
            }, 1500);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(err => {
        console.error('Lỗi:', err);
        showNotification('Lỗi xảy ra', 'error');
    });
}

function returnBook(bookId) {
    if (confirm('Bạn có chắc muốn trả cuốn sách này không?')) {
        fetch(`/return/${bookId}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showNotification(data.message, 'error');
            }
        });
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} show`;
    
    const icons = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    };
    
    notification.innerHTML = `
        <i class="${icons[type]}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function checkLogin() {
    // Kiểm tra xem có session không - nếu không thì redirect login
    fetch('/check-login')
    .then(r => r.json())
    .then(data => {
        if (!data.logged_in) {
            showNotification('Vui lòng đăng nhập', 'warning');
            setTimeout(() => {
                window.location.href = '/login';
            }, 1000);
            return false;
        }
        return true;
    })
    .catch(() => true);
    return true;
}

function openPdfViewer(bookId) {
    window.location.href = `/read/${bookId}`;
}

function downloadBook(bookId) {
    window.location.href = `/download/${bookId}`;
}