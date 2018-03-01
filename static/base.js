// Base UI scripts

// hide header if not top frame
document.addEventListener("readystatechange", function() {
    if (window != window.top) {
        document.querySelector("header").style.display = "none";
    }
});


