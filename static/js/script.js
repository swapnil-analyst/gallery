function toggleMenu(event, el) {
    event.stopPropagation(); // VERY IMPORTANT

    let menu = el.parentElement;
    let dropdown = menu.querySelector(".dropdown");

    // close others
    document.querySelectorAll(".dropdown").forEach(d => {
        if (d !== dropdown) d.style.display = "none";
    });

    dropdown.style.display =
        dropdown.style.display === "block" ? "none" : "block";
}

// click anywhere closes menu
document.addEventListener("click", function () {
    document.querySelectorAll(".dropdown").forEach(d => {
        d.style.display = "none";
    });
});

function deleteImage(btn) {
    let card = btn.closest(".card");
    card.remove();
}