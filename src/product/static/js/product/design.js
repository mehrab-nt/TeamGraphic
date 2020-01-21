function previewUploadFile(element, imgId) {
  if (element.files.length > 0) {
    preview = document.getElementById(imgId);
    fileName = element.files[0].name;
    fileExtension = fileName.replace(/^.*\./, '');
    if (element.files[0].size/1000/1000 < 10) {
      if (fileExtension == 'jpg' || fileExtension == 'jpeg') {
        preview.src = URL.createObjectURL(element.files[0]);
        preview.alt = element.files[0].name;
        preview.style.display = "block";
        pid = 'p' + imgId;
        document.getElementById(pid).innerHTML = '<b>' + (element.files[0].size / 1000 / 1000).toFixed(2) + '</b>‌MB' +
        ' .<b>' + fileExtension + '</b>';
//        readImageFile(element.files[0]);
      }
      else {
        element.value = "";
        preview.style.display = "none";
//        document.getElementById('fileInfo').innerHTML =
//            document.getElementById('fileInfo').innerHTML + '<br /> ' +
//                'Name: <b>' + fileName + '</b> <br />' +
//                'File Extension: <b>' + fileExtension + '</b> <br />' +
//                'Size: <b>' + Math.round((fileSize / 1000 / 1000)).toFixed(2) + '</b> MB <br />' +
//                'Type: <b>' + fileType + '</b> <br />' +
//                'Last Modified: <b>' + dateModified + '</b> <br />';
      }
    }
    else {
      preview.style.display = "none";
      element.value = "";
      document.getElementById('fileInfo').innerHTML = "nso";
    }
  }
  else {
    element.value = "";
    document.getElementById('fileInfo').innerHTML = "ndo";
  }
}

function readImageFile(file) {
  var reader = new FileReader(); // CREATE AN NEW INSTANCE.
  reader.onload = function (e) {
    var img = new Image();
    img.src = e.target.result;
    img.onload = function () {
    var w = this.width;
    var h = this.height;
//    document.getElementById('fileInfo').innerHTML =
//      document.getElementById('fileInfo').innerHTML + '<br /> ' +
//          'Name: <b>' + file.name + '</b> <br />' +
//          'File Extension: <b>' + fileExtension + '</b> <br />' +
//          'Size: <b>' + (file.size / 1000 / 1000).toFixed(2) + '</b> MB <br />' +
//          'Width: <b>' + w + '</b> <br />' +
//          'Height: <b>' + h + '</b> <br />' +
//          'Type: <b>' + file.type + '</b> <br />' +
//          'Last Modified: <b>' + file.lastModifiedDate + '</b> <br />';
      }
    };
  reader.readAsDataURL(file);
}

function validateUploadDesignForm() {
  var x = document.getElementsByClassName("design-file");
  var i = 0;
  while (x[i]) {
    if (x[i].value == "") {
      alt = document.getElementById("error");
      message = document.getElementById("error-msg");
      alt.style.opacity = "0.9";
      alt.style.visibility = "visible";
      message.innerHTML = "لطفا تمام فایل ها را آپلود نمایید...";
      return false;
    }
  i++;
  }
}

function validateReqDesignForm() {
  var x = document.getElementById("design-base");
  if (!(x.checked)) {
    alt = document.getElementById("error");
    message = document.getElementById("error-msg");
    alt.style.opacity = "0.9";
    alt.style.visibility = "visible";
    message.innerHTML = "لطفا یک گزینه جهت طراحی انتخاب کنید! یا اگر طرح دارید در منوی مربوطه فایل ها را آپلود نمایید...";
    return false;
  }
}

function setDesignPrice(element, designPrice, proPrice) {
  if (element.checked) {
      document.getElementById('design-price').innerHTML = setPerNum(designPrice);
      document.getElementById('total-price').innerHTML = setPerNum(designPrice + proPrice);
  }
  else {
      document.getElementById('design-price').innerHTML = '۰';
      document.getElementById('total-price').innerHTML = setPerNum(proPrice);
  }
}
