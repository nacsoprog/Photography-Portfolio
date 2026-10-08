document.addEventListener('DOMContentLoaded', () => {
  // Mobile Menu
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      mobileMenu.classList.toggle('open');
    });
  }

  // Email Copy functionality
  const emailBtn = document.getElementById('email-btn');
  const copyPopup = document.getElementById('copy-popup');
  
  if (emailBtn && copyPopup) {
    emailBtn.addEventListener('click', () => {
      navigator.clipboard.writeText('n_so@ucsb.edu').then(() => {
        copyPopup.classList.add('show');
        setTimeout(() => {
          copyPopup.classList.remove('show');
        }, 2000);
      });
    });
  }

  // Lightbox
  const lightbox = document.getElementById('lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  const lightboxNote = document.getElementById('lightbox-note');
  const closeBtn = document.querySelector('.lightbox-close');
  const prevBtn = document.querySelector('.lightbox-prev');
  const nextBtn = document.querySelector('.lightbox-next');
  
  if (!lightbox) return; // Not on a gallery page

  const galleryImages = Array.from(document.querySelectorAll('.masonry-item img'));
  let currentIndex = 0;

  function openLightbox(index) {
    currentIndex = index;
    const src = galleryImages[currentIndex].getAttribute('src');
    // If we are loading smaller images in masonry, we could swap to full res here.
    // Assuming the gallery images are already the high-res WebP versions based on the prompt.
    lightboxImg.setAttribute('src', src);
    lightboxNote.hidden = !galleryImages[currentIndex].parentElement.querySelector('.device-note');
    lightbox.classList.add('active');
  }

  function closeLightbox() {
    lightbox.classList.remove('active');
    lightboxImg.setAttribute('src', '');
  }

  function showPrev() {
    currentIndex = (currentIndex - 1 + galleryImages.length) % galleryImages.length;
    openLightbox(currentIndex);
  }

  function showNext() {
    currentIndex = (currentIndex + 1) % galleryImages.length;
    openLightbox(currentIndex);
  }

  galleryImages.forEach((img, index) => {
    img.addEventListener('click', () => openLightbox(index));
  });

  closeBtn.addEventListener('click', closeLightbox);
  prevBtn.addEventListener('click', showPrev);
  nextBtn.addEventListener('click', showNext);

  lightbox.addEventListener('click', (e) => {
    if (e.target === lightbox) {
      closeLightbox();
    }
  });

  document.addEventListener('keydown', (e) => {
    if (!lightbox.classList.contains('active')) return;
    if (e.key === 'Escape') closeLightbox();
    if (e.key === 'ArrowLeft') showPrev();
    if (e.key === 'ArrowRight') showNext();
  });
});
