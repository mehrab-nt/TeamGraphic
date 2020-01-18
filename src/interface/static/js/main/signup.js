"use strict";

var modal = document.getElementById('signup');
var modal2 = document.getElementById('forget');

window.onclick = function(event) {
  if (event.target === modal) {
    modal.style.display = "none";
  }
  if (event.target === modal2) {
    modal2.style.display = "none";
  }
}

function checkUsername(username='') {
  var message, alert;
  alert = document.getElementById("error");
  message = document.getElementById("error-msg");
  try {
    if(isNaN(username.value)) throw "لطفا شماره موبایل صحیح وارد نمایید";
    if((username.value[0] != 0) || (username.value[1] != 9)) throw "لطفا شماره موبایل صحیح وارد نمایید";
    if(username.value.length != 11) throw "لطفا شماره موبایل را کامل وارد نمایید";
  }
  catch(err) {
    alert.style.display = "block";
    alert.style.opacity = "0.9";
    message.innerHTML = err;
    username.value = '';
  }
  finally {

  }
}

// password name & ...

