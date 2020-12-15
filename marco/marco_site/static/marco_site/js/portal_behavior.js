/*
  This file is a result of not wanting to futz with the old WebPack Bootstrap
  logic that populates the .js files in "bundles".
  RDH 2020-12-15
*/

$(document).ready(function() {
  setTimeout(function() {
    // var badge = $('.badge');
    var badge_text = $('.badge-text');
    badge_text.each(function() {
      var btext = $(this);
      var badge = btext.parent();
      while (btext.width() > (badge.innerWidth())) {
        var font_size = btext.css('font-size');
        var new_size = parseInt(font_size)-1 + "px";
        btext.css('font-size', new_size);
      }
    });
  }, 100);
});
