document.addEventListener('DOMContentLoaded', function() {
    const cartCountElement = document.querySelector('.cart-count');
    let cartCount = 0;
    
    window.addToCart = function() {
        cartCount++;
        cartCountElement.textContent = cartCount;
        
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ تمت الإضافة';
        btn.style.backgroundColor = '#D4AF37';
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.backgroundColor = '';
        }, 2000);
    };

    window.addToWishlist = function() {
        const btn = event.target.closest('.btn');
        btn.classList.toggle('active');
        
        if (btn.querySelector('svg').getAttribute('fill') === 'currentColor') {
            btn.querySelector('svg').setAttribute('fill', 'none');
        } else {
            btn.querySelector('svg').setAttribute('fill', 'currentColor');
        }
    };

    const mainImage = document.querySelector('.main-image img');
    if (mainImage) {
        mainImage.addEventListener('mousemove', function(e) {
            const { left, top, width, height } = this.getBoundingClientRect();
            const x = (e.clientX - left) / width * 100;
            const y = (e.clientY - top) / height * 100;
            
            this.style.transformOrigin = `${x}% ${y}%`;
        });
    }

    const filterCheckboxes = document.querySelectorAll('.filter-group input[type="checkbox"]');
    filterCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            console.log('Filter changed:', this.value, this.checked);
        });
    });

    const sortSelect = document.querySelector('.sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            console.log('Sort changed:', this.value);
        });
    }

    const navLinks = document.querySelectorAll('.nav-links a');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            navLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });

    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header');
        if (window.scrollY > 50) {
            header.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.12)';
        } else {
            header.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.08)';
        }
    });
});
