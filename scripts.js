// scripts.js

document.addEventListener('DOMContentLoaded', function () {
  // Initialize the carousel
  if (document.getElementById('results-carousel')) {
    var carousel = document.getElementById('results-carousel');
    var carouselInstance = new BulmaCarousel(carousel, {
      slidesToScroll: 1,
      slidesToShow: 1,
      autoplay: true,
      interval: 3000
    });
  }
});
