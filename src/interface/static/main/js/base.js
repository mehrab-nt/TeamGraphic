function alertFunction(msg){
    var div = msg.parentElement;
    div.style.opacity = "0";
    setTimeout(function(){ div.style.display = "none"; }, 600);
}

function viewAlertFunction(){
    var alert_msg = document.getElementByClassName("closebtn");
    var i;
    for (i = 0; i < alert_msg.length; i++){
        alert_msg[i].parentElement.style.opacity = 1;
    }
}