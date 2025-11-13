document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("button[name='delete']").forEach(function (btn) {
    btn.addEventListener("click", function (event) {
      const confirmed = confirm("Are you sure you want to delete this item?");
      if (!confirmed) {
        event.preventDefault(); // stop form submission
      }
    });
  });
});
