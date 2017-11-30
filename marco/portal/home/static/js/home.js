$(document).ready(function() {
  $(".carousel").slick({
    accessibility: true,
    arrows: true,
    dots: true,
    // infinite: false,
    autoplay: true,
    autoplaySpeed: 5000,
    responsive: [{
      breakpoint: 1024,
      settings: {
          accessibility: false,
          arrows: true,
          dots: true,
          pauseOnHover: true,
          autoplay: true,
          autoplaySpeed: 5000,
        }
    },{
      breakpoint: 450,
      settings: "unslick" // destroys slick
    }]
  });
});
