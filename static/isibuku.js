document.addEventListener('DOMContentLoaded', function() {
    // Ambil elemen-elemen tombol
    const favoriteBtn = document.getElementById('favorite-btn');
    const shareBtn = document.getElementById('share-btn');
    const addToCartBtn = document.getElementById('add-to-cart-btn');
    const buyNowBtn = document.getElementById('buy-now-btn');
    
    // Ambil elemen stok dan keranjang
    const availableStockElement = document.getElementById('available-stock');
    const cartCountElement = document.getElementById('cartCount');
    let cartItemCount = 0; // State keranjang (asumsi diinisialisasi dari state global jika ada)

    // --- FUNGSI UTAMA ---
    
    /** Memperbarui lencana jumlah item di keranjang. */
    function updateCartCount() {
        cartCountElement.textContent = cartItemCount;
        // Tampilkan/Sembunyikan badge
        cartCountElement.style.display = cartItemCount > 0 ? 'block' : 'none';
    }
    
    /** Menangani klik tombol Favorite/Wishlist */
    if (favoriteBtn) {
        favoriteBtn.addEventListener('click', function() {
            this.classList.toggle('favorited');
            const action = this.classList.contains('favorited') ? 'ditambahkan ke' : 'dihapus dari';
            alert(`Buku telah ${action} Wishlist/Buku Favorit Anda!`);
        });
    }

    /** Menangani klik tombol Share (Simulasi) */
    if (shareBtn) {
        shareBtn.addEventListener('click', function() {
            const bookTitle = document.querySelector('.book-title-section h1').textContent;
            alert(`Link untuk buku "${bookTitle}" telah disalin dan siap dibagikan!`);
        });
    }

    /** Menangani klik tombol Tambah ke Keranjang */
    if (addToCartBtn && availableStockElement) {
        addToCartBtn.addEventListener('click', function() {
            let availableStock = parseInt(availableStockElement.textContent);
            
            if (availableStock > 0) {
                // Simulasi penambahan berhasil
                cartItemCount++; // Tambah item ke keranjang
                availableStock--; // Kurangi stok
                
                availableStockElement.textContent = availableStock; // Perbarui tampilan stok
                updateCartCount();

                alert(`1 item "Bumi Manusia" ditambahkan ke keranjang! Total item: ${cartItemCount}.`);
                console.log(`[KERANJANG] Sukses. Stok tersisa: ${availableStock}`);
            } else {
                alert("Maaf, stok buku ini sedang habis (0).");
                addToCartBtn.disabled = true; 
                addToCartBtn.style.opacity = 0.6;
            }
        });
    }
    
    /** Menangani klik tombol Beli Sekarang */
    if (buyNowBtn) {
        buyNowBtn.addEventListener('click', function() {
             let availableStock = parseInt(availableStockElement.textContent);
            
            if (availableStock > 0) {
                alert("Mengarahkan ke halaman Checkout untuk pembelian langsung!");
            } else {
                 alert("Maaf, tidak bisa Beli Sekarang, stok buku ini sedang habis (0).");
            }
        });
    }
    
    // Cek awal untuk status tombol dan keranjang
    updateCartCount();
    if (parseInt(availableStockElement.textContent) <= 0) {
        addToCartBtn.disabled = true;
        addToCartBtn.style.opacity = 0.6;
        buyNowBtn.disabled = true;
        buyNowBtn.style.opacity = 0.6;
    }
});