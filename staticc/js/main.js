// Main JavaScript file for E-commerce Store

// Global variables
let searchTimeout;

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

// Initialize application
function initializeApp() {
    initializeMobileMenu();
    initializeToasts();
    initializeSearchSuggestions();
    initializeLazyLoading();
    initializeScrollToTop();
}

// Mobile menu functionality
function initializeMobileMenu() {
    const mobileMenuButton = document.getElementById('mobile-menu-button');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!mobileMenuButton.contains(event.target) && !mobileMenu.contains(event.target)) {
                mobileMenu.classList.add('hidden');
            }
        });
    }
}

// Toast notification system
function initializeToasts() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(function(toast, index) {
        setTimeout(function() {
            toast.classList.remove('hide');
            toast.classList.add('show');
        }, index * 200);
        
        setTimeout(function() {
            toast.classList.remove('show');
            toast.classList.add('hide');
            setTimeout(function() {
                toast.remove();
            }, 300);
        }, 5000 + (index * 200));
    });
}

// Show toast notification
function showToast(message, type = 'info', duration = 5000) {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    const toast = document.createElement('div');
    
    const bgColor = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'warning': 'bg-yellow-500',
        'info': 'bg-blue-500'
    }[type] || 'bg-blue-500';
    
    const icon = {
        'success': 'fas fa-check-circle',
        'error': 'fas fa-exclamation-circle',
        'warning': 'fas fa-exclamation-triangle',
        'info': 'fas fa-info-circle'
    }[type] || 'fas fa-info-circle';
    
    toast.className = `${bgColor} text-white px-6 py-3 rounded-lg shadow-lg transform translate-x-full transition-transform duration-300 mb-2`;
    toast.innerHTML = `
        <div class="flex items-center">
            <i class="${icon} mr-2"></i>
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Animate in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 100);
    
    // Auto remove
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, duration);
}

// Create toast container if it doesn't exist
function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'fixed top-20 right-4 z-50 space-y-2';
    document.body.appendChild(container);
    return container;
}

// Search suggestions
function initializeSearchSuggestions() {
    const searchInputs = document.querySelectorAll('input[name="search"]');
    
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    fetchSearchSuggestions(query, this);
                }, 300);
            } else {
                hideSuggestions(this);
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(event) {
            if (!input.contains(event.target)) {
                hideSuggestions(input);
            }
        });
    });
}

// Fetch search suggestions
function fetchSearchSuggestions(query, inputElement) {
    // This would typically make an AJAX call to get suggestions
    // For now, we'll create a simple mock implementation
    const suggestions = [
        'Electronics',
        'Clothing',
        'Books',
        'Home & Garden',
        'Sports & Outdoors'
    ].filter(item => item.toLowerCase().includes(query.toLowerCase()));
    
    showSuggestions(suggestions, inputElement);
}

// Show search suggestions
function showSuggestions(suggestions, inputElement) {
    hideSuggestions(inputElement); // Remove existing suggestions
    
    if (suggestions.length === 0) return;
    
    const suggestionBox = document.createElement('div');
    suggestionBox.className = 'absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-b-md shadow-lg z-50 max-h-60 overflow-y-auto';
    suggestionBox.id = `suggestions-${inputElement.name}`;
    
    suggestions.forEach(suggestion => {
        const item = document.createElement('div');
        item.className = 'px-4 py-2 hover:bg-gray-100 cursor-pointer';
        item.textContent = suggestion;
        item.addEventListener('click', function() {
            inputElement.value = suggestion;
            hideSuggestions(inputElement);
            inputElement.form.submit();
        });
        suggestionBox.appendChild(item);
    });
    
    inputElement.parentElement.style.position = 'relative';
    inputElement.parentElement.appendChild(suggestionBox);
}

// Hide search suggestions
function hideSuggestions(inputElement) {
    const existingSuggestions = document.getElementById(`suggestions-${inputElement.name}`);
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
}

// Lazy loading for images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for browsers without IntersectionObserver
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Scroll to top button
function initializeScrollToTop() {
    const scrollButton = createScrollToTopButton();
    
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollButton.classList.remove('hidden');
        } else {
            scrollButton.classList.add('hidden');
        }
    });
}

// Create scroll to top button
function createScrollToTopButton() {
    const button = document.createElement('button');
    button.className = 'fixed bottom-6 right-6 bg-blue-600 text-white p-3 rounded-full shadow-lg hover:bg-blue-700 transition-colors duration-200 hidden z-40';
    button.innerHTML = '<i class="fas fa-arrow-up"></i>';
    button.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    document.body.appendChild(button);
    return button;
}

// Cart functionality
function addToCart(productId, quantity = 1) {
    if (!isUserAuthenticated()) {
        showToast('Please log in to add items to cart', 'warning');
        setTimeout(() => {
            window.location.href = '/accounts/login/';
        }, 2000);
        return;
    }
    
    fetch('/add-to-cart/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            'product_id': productId,
            'quantity': quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast(data.message, 'success');
            updateCartCount(data.cart_items_count);
        } else {
            showToast(data.message, 'error');
        }
    })
    .catch(error => {
        showToast('An error occurred', 'error');
    });
}

// Update cart count in navigation
function updateCartCount(count) {
    const cartLinks = document.querySelectorAll('a[href*="cart"]');
    cartLinks.forEach(link => {
        const badge = link.querySelector('.bg-red-500');
        if (badge) {
            if (count > 0) {
                badge.textContent = count;
            } else {
                badge.remove();
            }
        } else if (count > 0) {
            const icon = link.querySelector('i');
            if (icon) {
                const newBadge = document.createElement('span');
                newBadge.className = 'absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center';
                newBadge.textContent = count;
                link.appendChild(newBadge);
            }
        }
    });
}

// Utility functions
function isUserAuthenticated() {
    // This would check if user is authenticated
    // For now, we'll check if there's a user menu in the navigation
    return document.querySelector('.group button') !== null;
}

function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Form validation helpers
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    const re = /^[\+]?[1-9][\d]{0,15}$/;
    return re.test(phone.replace(/\s/g, ''));
}

// Price formatting
function formatPrice(price) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(price);
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for global use
window.showToast = showToast;
window.addToCart = addToCart;
window.updateCartCount = updateCartCount;
