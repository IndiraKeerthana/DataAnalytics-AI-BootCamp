document.addEventListener("DOMContentLoaded", function () {
    console.log("Complaint system loaded");

    const form = document.querySelector("form");

    form.addEventListener("submit", function () {
        alert("Complaint submitted successfully!");
    });
});