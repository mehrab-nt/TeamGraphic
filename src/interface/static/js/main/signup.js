var modal = document.getElementById('signup');
var modal2 = document.getElementById('forget');

window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
    if (event.target == modal2) {
        modal2.style.display = "none";
    }
}

