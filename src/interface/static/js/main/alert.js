"use strict";

//var close = document.getElementsByClassName("alert-closebtn");
//var i;
//
//for (i = 0; i < close.length; i++) {
//    close[i].onclick = function(){
//        var div = this.parentElement;
//        div.style.opacity = "0";
//        setTimeout(function(){ div.style.display = "none"; }, 600);
//    }
//}

function alertClose(sig) {
  var div = sig.parentElement
  div.style.opacity = "0";
  setTimeout(function(){ div.style.display = "none"; }, 600);
}

function alertAutoClose(sig) {
  sig.style.opacity = "0";
  setTimeout(function(){ sig.style.display = "none"; }, 100);
}