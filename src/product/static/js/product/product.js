function sizeChoose(element) {
  node = element.parentNode.firstChild;
  while (node) {
    if (node !== element && node.className !== "head-option" ) {
        node.className = "size-item default-item";
    }
    node = node.nextElementSibling || node.nextSibling;
  }
  element.className = "size-item active-item";
}

function readyChoose(element) {
  node = element.parentNode.firstChild;
  while (node) {
    if (node !== element && node.className !== "head-option-left" ) {
        node.className = "ready-item default-item";
    }
    node = node.nextElementSibling || node.nextSibling;
  }
  element.className = "ready-item active-item";
}

function test(element) {
    element.style.backgroundColor = 'red';
}