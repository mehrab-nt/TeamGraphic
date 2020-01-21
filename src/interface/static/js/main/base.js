"use strict";

document.getElementById("defaultOpen").click();

function openTabForm(mode, element, dy) {
  // Hide all elements with class="tabcontent" by default */
  var i, tabcontent, tablinks, inp;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
    if (dy) {
      inp = tabcontent[i].getElementsByTagName("input");
      if (inp[0].checked) {
        inp[0].click();
      }
    }
  }

  // Remove the background color of all tablinks/buttons
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].style.backgroundColor = "";
  }

  // Show the specific tab content
  document.getElementById(mode).style.display = "block";

  // Add the specific color to the button used to open the tab content
  element.style.backgroundColor = "#ffcc00";
  if (mode == 'uFile') {
    document.getElementById('design-submit').setAttribute("form" ,"upload-form");
  }
  else if (mode == 'rFile') {
    document.getElementById('design-submit').setAttribute("form" ,"design-form");
  }
}