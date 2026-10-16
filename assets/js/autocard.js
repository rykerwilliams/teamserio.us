// Card-image hover previews for any <a class="autocard" data-card="...">.
//
// Listeners are DELEGATED to document rather than bound per-link. The previous
// version ran querySelectorAll once on DOMContentLoaded, so any link added to
// the page afterwards got no preview -- which breaks every card on a page that
// renders its list in JS, like /vintage-legality.
document.addEventListener("DOMContentLoaded", function () {
  var tooltip = document.createElement("div");
  tooltip.className = "autocard-tooltip";
  tooltip.style.position = "absolute";
  tooltip.style.pointerEvents = "none";
  tooltip.style.display = "none";
  tooltip.style.zIndex = "1080";
  document.body.appendChild(tooltip);

  var current = null;

  function hide() {
    current = null;
    tooltip.style.display = "none";
    tooltip.innerHTML = "";
  }

  document.addEventListener("mouseover", function (e) {
    var link = e.target.closest && e.target.closest("a.autocard");
    if (!link || link === current) return;
    current = link;
    // Cached, de-duplicated, and null rather than a thrown error when the card
    // is double-faced or the name is not recognised.
    // "original" prefers the first printing. named?exact= returns Scryfall's
    // default, which is usually a modern reprint -- Black Lotus comes back as
    // Vintage Masters 2014 rather than Alpha.
    window.TSCards.image(link.dataset.card, "original").then(function (url) {
      // the pointer may have left, or moved to another card, while we waited
      if (!url || current !== link) return;
      var img = document.createElement("img");
      img.src = url;
      img.alt = "";
      img.style.maxWidth = "350px";
      img.style.border = "1px solid #333";
      img.style.borderRadius = "8px";
      // A page may want the preview to match how the card looks where it is
      // sitting -- /vintage-legality draws binder wear on both.
      var wrap = document.createElement("span");
      wrap.className = "autocard-wrap";
      wrap.appendChild(img);
      if (window.TSCards && typeof window.TSCards.tooltipDecorator === "function") {
        try { window.TSCards.tooltipDecorator(link, wrap); } catch (err) {}
      }
      tooltip.innerHTML = "";
      tooltip.appendChild(wrap);
      tooltip.style.display = "block";
    });
  });

  document.addEventListener("mouseout", function (e) {
    var link = e.target.closest && e.target.closest("a.autocard");
    if (link && link === current) hide();
  });

  document.addEventListener("mousemove", function (e) {
    if (tooltip.style.display === "none") return;
    // keep the preview inside the viewport instead of forcing a scrollbar
    var w = tooltip.offsetWidth || 350;
    var h = tooltip.offsetHeight || 490;
    var x = e.pageX + 15;
    var y = e.pageY + 15;
    var maxX = window.scrollX + window.innerWidth - w - 10;
    var maxY = window.scrollY + window.innerHeight - h - 10;
    tooltip.style.left = Math.max(window.scrollX + 5, Math.min(x, maxX)) + "px";
    tooltip.style.top = Math.max(window.scrollY + 5, Math.min(y, maxY)) + "px";
  });

  // a tap outside, or any scroll, dismisses a stuck preview on touch devices
  window.addEventListener("scroll", function () {
    if (tooltip.style.display !== "none") hide();
  }, { passive: true });
});
