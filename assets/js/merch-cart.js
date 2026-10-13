// Merch enquiry cart.
//
// This is not a shop. There is no checkout, no payment and no backend -- the
// site is static, so it cannot send anything anywhere. What it does is let you
// gather a few items and copy a tidy summary to the clipboard, which you then
// paste to the maker on Slack or Discord.
//
// Deliberately no email addresses anywhere. A mailto: link would put the
// maker's address in the page source for scrapers to harvest; assembling it in
// JavaScript only slows that down, since the address is still in the file.
// Copying to the clipboard keeps contact on channels the group already uses.
(function () {
  "use strict";

  var KEY = "ts-merch-cart-v1";
  var cart = load();

  function load() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(v) ? v : [];
    } catch (e) {
      return [];
    }
  }

  function save() {
    try {
      localStorage.setItem(KEY, JSON.stringify(cart));
    } catch (e) {
      /* private mode or quota: the cart still works for this page view */
    }
    paint();
  }

  function add(item) {
    var found = cart.filter(function (c) {
      return c.slug === item.slug;
    })[0];
    if (found) {
      found.qty += 1;
    } else {
      item.qty = 1;
      cart.push(item);
    }
    save();
  }

  function remove(slug) {
    cart = cart.filter(function (c) { return c.slug !== slug; });
    save();
  }

  // Prices are free text so "25", "$25", "trade" and "ask" all work. Pull out a
  // number where there is one; everything else is left as written and simply
  // does not count towards the total.
  function amount(price) {
    var m = String(price || "").match(/-?\d+(?:[.,]\d+)?/);
    return m ? parseFloat(m[0].replace(",", ".")) : null;
  }

  // One block per maker, so a cart spanning two people gives you two things to
  // paste rather than one message naming someone else's items.
  function summary() {
    var makers = {};
    cart.forEach(function (c) {
      (makers[c.creator] = makers[c.creator] || []).push(c);
    });
    return Object.keys(makers).sort().map(function (who) {
      var width = Math.max.apply(null, makers[who].map(function (c) {
        return (c.qty + "x  " + c.title).length;
      }));
      var total = 0, counted = 0, uncounted = 0, symbol = "";
      var lines = makers[who].map(function (c) {
        var label = c.qty + "x  " + c.title;
        var pad = new Array(Math.max(1, width - label.length + 3)).join(" ");
        var n = amount(c.price);
        if (n === null) {
          if (c.price) uncounted += 1;
          return "  " + label + (c.price ? pad + c.price : "");
        }
        // Reuse whatever symbol the prices are written with, rather than
        // assuming one. These are friends in more than one country.
        if (!symbol) {
          var sym = String(c.price).match(/^[^\d\s-]+/);
          if (sym) symbol = sym[0];
        }
        total += n * c.qty;
        counted += 1;
        return "  " + label + pad + c.price + (c.qty > 1 ? " ea" : "");
      });
      var handle = makers[who][0].handle;
      var foot = "";
      if (counted) {
        foot = "\n  roughly " + symbol + (Math.round(total * 100) / 100) +
               (uncounted ? "  (plus the items priced otherwise)" : "") + "\n";
      }
      return "Team Serious merch — enquiry for " + who +
             (handle ? " (" + handle + ")" : "") + "\n\n" +
             lines.join("\n") + "\n" + foot + "\n" +
             "  from " + window.location.origin + "/merch/";
    }).join("\n\n----\n\n");
  }

  function paint() {
    var count = cart.reduce(function (n, c) { return n + c.qty; }, 0);
    document.querySelectorAll("[data-cart-count]").forEach(function (el) {
      el.textContent = count;
      el.closest("[data-cart-wrap]") &&
        el.closest("[data-cart-wrap]").classList.toggle("d-none", count === 0);
    });

    var list = document.querySelector("[data-cart-list]");
    if (!list) return;
    list.textContent = "";
    if (!cart.length) {
      var p = document.createElement("p");
      p.className = "text-muted mb-0";
      p.textContent = "Nothing in the cart yet.";
      list.appendChild(p);
    } else {
      cart.forEach(function (c) {
        var row = document.createElement("div");
        row.className = "d-flex justify-content-between align-items-center border-bottom py-2";
        var left = document.createElement("span");
        left.textContent = c.qty + "× " + c.title + " — " + c.creator;
        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn btn-sm btn-outline-secondary";
        btn.textContent = "Remove";
        btn.addEventListener("click", function () { remove(c.slug); });
        row.appendChild(left);
        row.appendChild(btn);
        list.appendChild(row);
      });
    }
    var out = document.querySelector("[data-cart-summary]");
    if (out) out.value = summary();
  }

  document.addEventListener("click", function (ev) {
    var addBtn = ev.target.closest && ev.target.closest("[data-merch-add]");
    if (addBtn) {
      ev.preventDefault();
      add({
        slug: addBtn.dataset.merchAdd,
        title: addBtn.dataset.merchTitle || addBtn.dataset.merchAdd,
        creator: addBtn.dataset.merchCreator || "Team Serious",
        handle: addBtn.dataset.merchHandle || "",
        price: addBtn.dataset.merchPrice || ""
      });
      addBtn.textContent = "Added ✓";
      setTimeout(function () { addBtn.textContent = "Add to enquiry"; }, 1400);
      return;
    }

    var clear = ev.target.closest && ev.target.closest("[data-cart-clear]");
    if (clear) {
      ev.preventDefault();
      cart = [];
      save();
      return;
    }

    var copy = ev.target.closest && ev.target.closest("[data-cart-copy]");
    if (copy) {
      ev.preventDefault();
      if (!cart.length) return;
      var text = summary();
      var done = function () {
        copy.textContent = "Copied ✓";
        setTimeout(function () { copy.textContent = "Copy enquiry"; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, fallback);
      } else {
        fallback();
      }
      function fallback() {
        // Older browsers, and any page not served over https, have no
        // navigator.clipboard. Select the textarea instead so the summary can
        // be copied by hand rather than the button doing nothing.
        var ta = document.querySelector("[data-cart-summary]");
        if (!ta) return;
        ta.focus();
        ta.select();
        try { document.execCommand("copy"); done(); } catch (e) { /* user copies manually */ }
      }
    }
  });

  document.addEventListener("DOMContentLoaded", paint);
  paint();
})();
