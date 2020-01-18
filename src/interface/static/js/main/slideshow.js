"use strict";

var slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n=1) {
  showSlides(slideIndex += n);
}

function currentSlide(n=1) {
  showSlides(slideIndex = n);
}

function showSlides(n=1) {
  var i;
  var slides = document.getElementsByClassName("slide");
//  var dots = document.getElementsByClassName("demo");
//  var captionText = document.getElementById("caption");
  if (n > slides.length) {
    slideIndex = 1
  }
  if (n < 1) {
    slideIndex = slides.length
  }
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
    slides[i].style.transition = 'opacity 1s';
  }
//  for (i = 0; i < dots.length; i++) {
//    dots[i].className = dots[i].className.replace(" active", "");
//  }
  slides[slideIndex-1].style.display = "block";
  slides[slideIndex-1].style.transition = 'opacity 1s';
//  dots[slideIndex-1].className += " active";
//  captionText.innerHTML = dots[slideIndex-1].alt;
}