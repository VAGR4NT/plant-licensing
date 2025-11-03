document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector(".searchForm");
  if (!form) return;

  // Before form submission, mark that we should scroll after reload
  form.addEventListener("submit", function () {
    sessionStorage.setItem("scrollToResults", "true");
  });
});

window.addEventListener("load", function () {
  // Check if we should scroll after reload
  if (sessionStorage.getItem("scrollToResults") === "true") {
    sessionStorage.removeItem("scrollToResults"); // reset the flag

    const resultsSection = document.querySelector("#results");
    if (resultsSection) {
      // Disable all smooth scrolling and jump instantly
      document.documentElement.style.scrollBehavior = "auto";
      document.body.style.scrollBehavior = "auto";

      // Force an immediate scroll to the results section
      window.scrollTo({
        top: resultsSection.offsetTop,
        behavior: "auto",
      });
    }
  }
});
