function sizeChoose(element) {
  var node = element.parentNode.firstChild;
  while (node) {
    if (node !== element && node.className !== "head-option" ) {
        node.className = "size-item default-item";
    }
    node = node.nextElementSibling || node.nextSibling;
  }
  element.className = "size-item active-item";
  var allPrice = document.getElementsByClassName("price-item");
  var j = 0;
  while (allPrice[j]) {
    allPrice[j].style.display = 'none';
    j++;
  }
  var allCount = document.getElementsByClassName("count-item");
  j = 0;
  while (allCount[j]) {
    allCount[j].style.display = 'none';
    j++;
  }
  var size = document.getElementsByClassName("size-item active-item");
  var ready = document.getElementsByClassName("ready-item active-item");
  var tmp = ready[0].id + size[0].id;
  var temp = document.getElementsByClassName(tmp);
  var i = 0;
  while (temp[i]) {
    temp[i].style.display = 'block';
    i++;
  }
//  var check = document.getElementsByClassName("price-check");
//  i = 0;
//  while (check[i]) {
//    check[i].checked = false;
//    i++;
//  }
}

function readyChoose(element) {
  var node = element.parentNode.firstChild;
  while (node) {
    if (node !== element && node.className !== "head-option-left") {
        node.className = "ready-item default-item";
    }
    node = node.nextElementSibling || node.nextSibling;
  }
  element.className = "ready-item active-item";
  var allPrice = document.getElementsByClassName("price-item");
  var j = 0;
  while (allPrice[j]) {
    allPrice[j].style.display = 'none';
    j++;
  }
  var allCount = document.getElementsByClassName("count-item");
  j = 0;
  while (allCount[j]) {
    allCount[j].style.display = 'none';
    j++;
  }
  var size = document.getElementsByClassName("size-item active-item");
  var ready = document.getElementsByClassName("ready-item active-item");
  var tmp = ready[0].id + size[0].id;
  var temp = document.getElementsByClassName(tmp);
  var i = 0;
  while (temp[i]) {
    temp[i].style.display = 'block';
    i++;
  }
//  var check = document.getElementsByClassName("price-check");
//  i = 0;
//  while (check[i]) {
//    check[i].checked = false;
//    i++;
//  }
}

function setPerNum(enNum) {
  num = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
  output = '';
  strPrice = String(enNum);
  for (var i = 0; i<strPrice.length; i++) {
    if ('0' <= strPrice[i] <= '9') {
      output += num[Number(strPrice[i])];
    }
    else {
      output += strPrice[i];
    }
  }
  return output;
}

function setTotalPrice() {
  var totalPriceContainer = document.getElementById("total-price");
  allService = document.getElementsByClassName("service-check");
  var j = 0;
  var val = 0;
  while (allService[j]) {
    if (allService[j].checked) {
     val += Number(allService[j].id);
    }
    j++;
  }
  allPrice = document.getElementsByClassName("price-check");
  j = 0;
  var price = 0;
  while (allPrice[j]) {
    if (allPrice[j].checked) {
     price += Number(allPrice[j].id);
     val *= Number(allPrice[j].className[17])
     break;
    }
    j++;
  }
  totalPriceContainer.innerHTML = setPerNum(val + price);
}

function setPrice(element) {
  var priceContainer = document.getElementById("product-price");
  priceContainer.innerHTML = setPerNum(element.id);
  setServicePrice();
  setTotalPrice();
}

function setServicePrice() {
  var servicePriceContainer = document.getElementById("service-price");
  allService = document.getElementsByClassName("service-check");
  var j = 0;
  val = 0;
  while (allService[j]) {
    if (allService[j].checked) {
     val += Number(allService[j].id);
    }
    j++;
  }
  allPrice = document.getElementsByClassName("price-check");
  j = 0;
  var price = 0;
  while (allPrice[j]) {
    if (allPrice[j].checked) {
     val *= Number(allPrice[j].className[17])
     break;
    }
    j++;
  }
  servicePriceContainer.innerHTML = setPerNum(val);
  setTotalPrice();
}

window.addEventListener("load", function(){
  var sizeElement = document.getElementById("size-container");
  var sizeNode = sizeElement.firstChild;
  var readyElement = document.getElementById("ready-container");
  var readyNode = readyElement.firstChild;
  while (sizeNode) {
    if (sizeNode.className === "head-option") {
      sizeNode.nextElementSibling.className = "size-item active-item";
      break;
    }
    sizeNode = sizeNode.nextElementSibling || sizeNode.nextSibling;
  }
  while (readyNode) {
    if (readyNode.className === "head-option-left") {
      readyNode.nextElementSibling.className = "ready-item active-item";
      break;
    }
    readyNode = readyNode.nextElementSibling || readyNode.nextSibling;
  }
    var size = document.getElementsByClassName("size-item active-item");
    var ready = document.getElementsByClassName("ready-item active-item");
    var tmp = ready[0].id + size[0].id;
    var temp = document.getElementsByClassName(tmp);
    var i = 0;
    while (temp[i]) {
      temp[i].style.display = 'block';
      i++;
    }
    var check = document.getElementsByClassName("service-check");
    i = 0;
    while (check[i]) {
      check[i].checked = false;
      i++;
    }
    check = document.getElementsByClassName("price-check");
    i = 0;
    while (check[i]) {
      check[i].checked = false;
      i++;
    }
    check = document.getElementsByClassName("price-def");
    check[0].checked = true;
    setPrice(check[0]);
});

function signupFirstMassage() {
  var message, alert;
  alert = document.getElementById("warning");
  message = document.getElementById("warning-msg");
  alert.style.display = "block";
  alert.style.opacity = "0.9";
  message.innerHTML = "لطفا ابتدا <b>وارد</b> شوید. (اکانت کاربری ندارد؟ به راحتی ثبت نام کنید!!)";
}