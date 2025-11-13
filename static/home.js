document.addEventListener("DOMContentLoaded", () => {
  const toggleBtn = document.getElementById("toggleSidebar");
  const sidebar = document.querySelector(".sidebar");
  const icon = toggleBtn.querySelector("i");

  toggleBtn.addEventListener("click", () => {
    sidebar.classList.toggle("hide");
    // Ganti ikon antara "bars" dan "x"
    if (sidebar.classList.contains("hide")) {
      icon.classList.remove("fa-times");
      icon.classList.add("fa-bars");
    } else {
      icon.classList.remove("fa-bars");
      icon.classList.add("fa-times");
    }
  });
});

// FILTER GENRE
document.addEventListener('DOMContentLoaded', () => {
  const genreBtns = document.querySelectorAll('.genre-btn');
  const books = document.querySelectorAll('.book-card');

  function showAll() {
    books.forEach(b => {
      b.classList.remove('hidden');
      // reset ukuran jika sebelumnya di-skip
      b.style.height = '';
      b.style.padding = '';
      b.style.margin = '';
    });
  }

  function filterGenre(genre) {
    if (genre === 'all') {
      showAll();
      return;
    }

    books.forEach(card => {
      const genres = (card.dataset.genre || '').toLowerCase().split(',').map(s => s.trim());
      if (genres.includes(genre)) {
        card.classList.remove('hidden');
      } else {
        card.classList.add('hidden');
      }
    });
  }

  genreBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // aktifkan tampilan tombol
      genreBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const genre = btn.dataset.genre.toLowerCase();
      filterGenre(genre);
    });
  });
});