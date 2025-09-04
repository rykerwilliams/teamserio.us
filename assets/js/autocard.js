document.addEventListener("DOMContentLoaded", function() {
  const tooltip = document.createElement("div");
  tooltip.style.position = "absolute";
  tooltip.style.pointerEvents = "none";
  tooltip.style.display = "none";
  document.body.appendChild(tooltip);

  document.querySelectorAll("a.autocard").forEach(link => {
    let img;
    link.addEventListener("mouseenter", async e => {
      const cardName = link.dataset.card;
      const resp = await fetch(`https://api.scryfall.com/cards/named?exact=${encodeURIComponent(cardName)}`);
      const data = await resp.json();
      img = document.createElement("img");
      img.src = data.image_uris.normal;
      img.style.maxWidth = "250px";
      img.style.border = "1px solid #333";
      img.style.borderRadius = "8px";
      tooltip.innerHTML = "";
      tooltip.appendChild(img);
      tooltip.style.display = "block";
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