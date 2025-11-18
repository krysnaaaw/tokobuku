document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const sidebar = document.getElementById('sidebar');
    const cartCountElement = document.getElementById('cartCount');
    const navLinks = document.querySelectorAll('.sidebar-nav a[data-action]');
    const buyButtons = document.querySelectorAll('.btn-buy');
    const cartIcon = document.getElementById('cartIcon');

    // State Keranjang
    let cartItemCount = 0;

    // --- FUNGSI UTAMA ---

    /** Memperbarui lencana jumlah item di keranjang. */
    function updateCartCount() {
        cartCountElement.textContent = cartItemCount;
        // Tampilkan/Sembunyikan badge
        cartCountElement.style.display = cartItemCount > 0 ? 'block' : 'none';
    }

    /** Menangani klik tombol "Tambah ke Keranjang". */
    function handleAddToCart(event) {
        event.preventDefault();
        const bookId = event.target.getAttribute('data-book-id');
        cartItemCount++;
        updateCartCount();
        
        // Simulasikan notifikasi
        console.log(`[KERANJANG] Buku ID ${bookId} ditambahkan. Total: ${cartItemCount} item.`);
    }

    /** Menangani klik pada tautan Sidebar yang memerlukan tindakan sistem. */
    function handleSidebarAction(event) {
        event.preventDefault();
        const action = event.currentTarget.getAttribute('data-action');
        let message = '';

        switch (action) {
            case 'kategori':
                message = "Halaman Telusuri Kategori terbuka. Filter berdasarkan genre!";
                break;
            case 'pesanan':
                message = "Anda sedang mengecek Status Pesanan. Data pesanan Anda sedang dimuat...";
                break;
            case 'wishlist':
                message = "Halaman Wishlist terbuka. Daftar buku impian Anda ada di sini.";
                break;
            case 'diskusi':
                message = "Anda masuk ke Forum Diskusi. Ajukan pertanyaan atau baca ulasan komunitas.";
                break;
            default:
                message = "Aksi navigasi tidak dikenal.";
        }
        
        // Menggunakan alert hanya untuk demonstrasi fungsionalitas
        alert(`[SISTEM] ${message}`);
        console.log(`[NAVIGASI] Aksi: ${action}, Pesan: ${message}`);

        // Jika di mobile, tutup sidebar setelah klik
        if (window.innerWidth <= 768) {
             sidebar.classList.remove('visible');
        }
    }
    
    /** Menangani klik ikon Keranjang di header. */
    function handleCartView(event) {
        event.preventDefault();
        if (cartItemCount > 0) {
             alert(`Membuka halaman Keranjang. Total ada ${cartItemCount} item.`);
        } else {
             alert("Keranjang Anda kosong.");
        }
    }

    // --- INISIALISASI EVENT LISTENERS ---

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

    // 3. Listeners untuk Sidebar Actions (Kategori, Pesanan, Wishlist, Diskusi)
    navLinks.forEach(link => {
        link.addEventListener('click', handleSidebarAction);
    });

    // 4. Listeners untuk Tombol 'Tambah ke Keranjang'
    buyButtons.forEach(button => {
        button.addEventListener('click', handleAddToCart);
    });
    
    // 5. Listener untuk Ikon Keranjang di Header
    cartIcon.addEventListener('click', handleCartView);

    // Initial check for cart count display
    updateCartCount();
});