const container = document.querySelector(".column_container");
const dots = document.querySelectorAll(".carousel-indicators .dot");
if (container && dots.length) {
  container.addEventListener("scroll", () => {
    const boxes = document.querySelectorAll(".column_box");
    const containerRect = container.getBoundingClientRect();
    let activeIndex = 0;
    let minDiff = Infinity;

    boxes.forEach((box, i) => {
      const boxRect = box.getBoundingClientRect();
      const diff = Math.abs(
        boxRect.left +
          boxRect.width / 2 -
          (containerRect.left + containerRect.width / 2),
      );
      if (diff < minDiff) {
        minDiff = diff;
        activeIndex = i;
      }
    });

    dots.forEach((dot, i) => {
      dot.classList.toggle("active", i === activeIndex);
    });
  });
}
