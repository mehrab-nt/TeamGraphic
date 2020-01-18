"use strict";
window.onscroll = function() {stickyNavbar()};
var navbar = document.getElementById("navbar");
var sticky = navbar.offsetTop;

function mobileNavbar(arg) {
  var x = document.getElementById("tg_top_menu");
  if (x.className === "top_menu") {
    x.className += " responsive";
  }
  else {
    x.className = "top_menu";
  }
  if (arg.className === "sub_menu") {
    arg.className += " active";
  }
  else {
    arg.className = "sub_menu";
  }
}

function stickyNavbar() {
  if (window.pageYOffset >= sticky) {
    navbar.classList.add("sticky")
  } else {
    navbar.classList.remove("sticky");
  }
}