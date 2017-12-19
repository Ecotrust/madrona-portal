$(document).ready(function() {
  $(".carousel").slick({
    arrows: true,
    dots: true,
    // infinite: false,
    autoplay: true,
    autoplaySpeed: 5000,
    responsive: [{
      breakpoint: 1024,
      settings: {
          arrows: true,
          dots: true,
          pauseOnHover: true,
          autoplay: true,
          autoplaySpeed: 5000,
        }
    },{
      breakpoint: 700,
      settings: {
          arrows: true,
          dots: true,
          pauseOnHover: true,
          autoplay: true,
          autoplaySpeed: 5000,
        }
    },{
      breakpoint: 480,
      settings: {
        arrows: false,
        dots: false,
        pauseOnHover: false,
        autoplay: false,
      }
    }]
  });
});
