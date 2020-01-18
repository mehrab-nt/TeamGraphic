function sizeChoose(element) {
  var node = element.parentNode.firstChild;
  while (node) {
    if (node !== element && node.className !== "head-option" ) {
        node.className = "size-item default-item";
    }
    node = node.nextElementSibling || node.nextSibling;
  }
  element.className = "size-item active-item";
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
  var size = document.getElementsByClassName("size-item active-item");
  var ready = document.getElementsByClassName("ready-item active-item");
  var tmp = ready[0].id + size[0].id;
  var temp = document.getElementsByClassName(tmp);
  var i = 0;
  while (temp[i]) {
    temp[i].style.display = 'block';
    i++;
  }
}

// todo: hi :/

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
});