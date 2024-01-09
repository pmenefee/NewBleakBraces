document.addEventListener("DOMContentLoaded", function () {
  loadSidebar();
  setupQueryForm();
});

function loadSidebar() {
  fetch("static/menu.html")
    .then((response) => response.text())
    .then((html) => {
      document.getElementById("sidebar-placeholder").innerHTML = html;
    })
    .catch((error) => console.error("Error loading sidebar:", error));
}