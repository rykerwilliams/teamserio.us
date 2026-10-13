document.addEventListener("DOMContentLoaded", function () {
  // One delegated listener rather than one per link. An event report here can
  // carry 332 card links, and a decklist page several hundred more.
  var HOVER_DELAY = 120;   // so running the cursor down a list fetches nothing
  var timer = null;

  document.addEventListener("mouseover", function (ev) {
    var link = ev.target.closest && ev.target.closest(".card-link");
    if (!link) return;

    var name = link.getAttribute("data-cardname");
    var pane = link.closest(".decklist-content");
    pane = pane && pane.querySelector(".card-preview");
    if (!name || !pane) return;

    if (timer) clearTimeout(timer);
    timer = setTimeout(function () {
      // Cached and de-duplicated; resolves to null rather than throwing on a
      // double-faced card or a name Scryfall does not recognise.
      window.TSCards.image(name, "original").then(function (url) {
        if (url) pane.style.setProperty("background-image", "url(" + url + ")");
      });
    }, HOVER_DELAY);
  });
});

function copyDecklist(button) {
  // Find the sibling div with class 'copyable-decklist'
  const copyableDecklist = button.closest('.decklist-content').querySelector('.copyable-decklist').innerText;


  // Create a temporary textarea to hold the text
  const tempTextArea = document.createElement("textarea");
  tempTextArea.value = copyableDecklist;

  // Append the textarea to the document body
  document.body.appendChild(tempTextArea);

  // Select the text and copy it to the clipboard
  tempTextArea.select();
  document.execCommand("copy");

  // Remove the temporary textarea from the document
  document.body.removeChild(tempTextArea);

  // Optional: Provide feedback to the user
  alert("Decklist copied to clipboard!");
}