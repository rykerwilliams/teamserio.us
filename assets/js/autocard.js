document.addEventListener("DOMContentLoaded", function() {
  const tooltip = document.createElement("div");
  tooltip.style.position = "absolute";
  tooltip.style.pointerEvents = "none";
  tooltip.style.display = "none";
  document.body.appendChild(tooltip);

  document.querySelectorAll("a.autocard").forEach(link => {
    let img;
    link.addEventListener("mouseenter", function () {
      // Cached, de-duplicated, and null rather than a thrown error when the card
      // is double-faced or the name is not recognised.
      // "original" prefers the first printing. named?exact= returns Scryfall's
      // default, which is usually a modern reprint -- Black Lotus comes back as
      // Vintage Masters 2014 rather than Alpha.
      window.TSCards.image(link.dataset.card, "original").then(function (url) {
        if (!url) return;
        img = document.createElement("img");
        img.src = url;
        img.alt = "";
        img.style.maxWidth = "350px";
        img.style.border = "1px solid #333";
        img.style.borderRadius = "8px";
        tooltip.innerHTML = "";
        tooltip.appendChild(img);
        tooltip.style.display = "block";
      });
    });
    link.addEventListener("mousemove", e => {
      tooltip.style.left = e.pageX + 15 + "px";
      tooltip.style.top = e.pageY + 15 + "px";
    });
    link.addEventListener("mouseleave", () => {
      tooltip.style.display = "none";
    });
  });
});