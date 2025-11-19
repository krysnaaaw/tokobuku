document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const cartCountElement = document.getElementById('cartCount');
    const navLinks = document.querySelectorAll('.sidebar-nav a[data-action]');
    const bookCards = document.querySelectorAll('.book-card'); // Pilih semua book-card
    const cartIcon = document.getElementById('cartIcon');

    // State Keranjang (masih dipertahankan untuk ikon di header)
    let cartItemCount = 0;

    // --- FUNGSI UTAMA ---

    /** Memperbarui lencana jumlah item di keranjang. */
    function updateCartCount() {
        cartCountElement.textContent = cartItemCount;
        // Tampilkan/Sembunyikan badge
        cartCountElement.style.display = cartItemCount > 0 ? 'block' : 'none';
    }   
        alert(`[SISTEM] ${message}`);
        console.log(`[NAVIGASI] Aksi: ${action}, Pesan: ${message}`);

        if (window.innerWidth <= 768) {
            sidebar.classList.remove('visible');
        }
    }

    // 1. Sidebar Toggle (Mobile)
    if (menuToggle && sidebar) {
        menuToggle.addEventListener('click', function() {
            sidebar.classList.toggle('visible');
        });
    }

    // 2. Sidebar Close on Outside Click (Mobile)
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768) { 
            const isClickInsideSidebar = sidebar.contains(event.target);
            const isClickOnToggle = menuToggle && menuToggle.contains(event.target);

            if (sidebar.classList.contains('visible') && !isClickInsideSidebar && !isClickOnToggle) {
                sidebar.classList.remove('visible');
            }
        }
    });

    // Initial check for cart count display
    updateCartCount();
});