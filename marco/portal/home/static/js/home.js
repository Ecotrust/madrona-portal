$(".carousel").slick({
  responsive: [{
    breakpoint: 1024,
    settings: {
        slidesToShow: 1,
        infinite: true,
        dots: true,
        autoplay: true,
        autoplaySpeed: 6000,
      }
  },{
    breakpoint: 300,
    settings: "unslick" // destroys slick
  }]
});
