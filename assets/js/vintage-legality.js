// /vintage-legality -- replays the B&R event list and renders the state at
// whichever announcement is in view.
//
// The timeline rail is rendered server-side by Liquid, so the page is complete
// and readable without this script. Everything here is enhancement.
(function () {
  "use strict";

  var dataEl = document.getElementById("vl-data");
  var stateEl = document.getElementById("vl-state");
  if (!dataEl || !stateEl) return;

  var DATA = JSON.parse(dataEl.textContent);
  var EVENTS = DATA.events.slice().sort(function (a, b) { return a.seq - b.seq; });
  var CARDS = DATA.cards || {};
  var CATS = DATA.categories || [];
  var SOURCES = DATA.sources || {};

  // ---- replay -------------------------------------------------------------
  // state[i] is the list as it stood after EVENTS[i]. Precomputed once: 47
  // steps over ~150 actions is trivial and makes scrolling allocation-free.
  var STATES = [];
  (function build() {
    var restricted = [], banned = [];
    EVENTS.forEach(function (ev) {
      var added = [], removed = [];
      ev.actions.forEach(function (a) {
        var ri = restricted.indexOf(a.card), bi = banned.indexOf(a.card);
        if (a.action === "restrict") {
          if (ri < 0) { restricted.push(a.card); added.push(a.card); }
          if (bi >= 0) banned.splice(bi, 1);
        } else if (a.action === "unrestrict") {
          if (ri >= 0) { restricted.splice(ri, 1); removed.push(a.card); }
        } else if (a.action === "ban") {
          if (bi < 0) banned.push(a.card);
          if (ri >= 0) { restricted.splice(ri, 1); removed.push(a.card); }
        } else if (a.action === "unban") {
          if (bi >= 0) banned.splice(bi, 1);
        }
      });
      STATES.push({
        restricted: restricted.slice().sort(cmp),
        banned: banned.slice().sort(cmp),
        added: added, removed: removed
      });
    });
  })();

  function cmp(a, b) { return a.localeCompare(b); }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;",
               '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // a card name, as an autocard hover link that also opens its history
  function cardLink(name, cls) {
    return '<a href="#" class="autocard vl-hist-open' + (cls ? " " + cls : "") +
           '" data-card="' + esc(name) + '">' + esc(name) + "</a>";
  }

  // ---- dates --------------------------------------------------------------
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"];

  function prettyDate(ev) {
    var p = ev.date.split("-");
    if (ev.precision === "day") {
      return MONTHS[+p[1] - 1] + " " + (+p[2]) + ", " + p[0];
    }
    if (ev.precision === "month") return MONTHS[+p[1] - 1] + " " + p[0];
    return p[0];
  }

  // Say plainly what the date is and is not. 29 of 47 announcements do not
  // record whether their date is the announcement or the effective date, and
  // only 18 are day-precise -- the page must not imply precision it lacks.
  function basisNote(ev) {
    var bits = [];
    if (ev.basis === "effective") bits.push("effective date");
    else if (ev.basis === "announced") bits.push("announcement date");
    else bits.push("date basis unrecorded — may be announcement or effective");
    if (ev.precision === "month") bits.push("exact day unknown");
    else if (ev.precision === "year") bits.push("month and day unknown");
    return bits.join(" · ");
  }

  // ---- Scryfall legal pool ------------------------------------------------
  // Excludes by NAME, not by is:ante -- Scryfall has no such filter and
  // silently ignores an unknown is: term, so that query would quietly match
  // everything while looking like it worked.
  function poolQuery(ev, st) {
    var cutoff = ev.date.split("-");
    while (cutoff.length < 3) cutoff.push(cutoff.length === 1 ? "12" : "31");
    var terms = ["game:paper", "date<=" + cutoff.join("-"),
                 "-is:funny", "-is:digital", "-t:conspiracy"];
    var names = {};
    st.banned.forEach(function (n) { names[n] = 1; });
    CATS.forEach(function (c) {
      if (!c.cards) return;
      // a category only applies once it exists
      if (c.since && c.since > ev.date) return;
      c.cards.forEach(function (n) { names[n] = 1; });
    });
    Object.keys(names).sort(cmp).forEach(function (n) {
      terms.push('-!"' + n + '"');
    });
    return terms.join(" ");
  }

  // ---- render -------------------------------------------------------------
  function render(i) {
    var ev = EVENTS[i], st = STATES[i];
    var h = [];

    h.push('<h2 class="vl-asof">' + esc(prettyDate(ev)) + "</h2>");
    h.push('<p class="vl-basis">' + esc(basisNote(ev)) + "</p>");

    h.push('<div class="vl-count">' + st.restricted.length +
           " restricted · announcement " + ev.seq + " of " + EVENTS.length +
           "</div>");

    if (st.added.length || st.removed.length) {
      h.push('<div class="vl-delta">');
      st.added.slice().sort(cmp).forEach(function (n) {
        h.push('<div class="vl-add">' + cardLink(n) + "</div>");
      });
      st.removed.slice().sort(cmp).forEach(function (n) {
        h.push('<div class="vl-rem">' + cardLink(n) + "</div>");
      });
      h.push("</div>");
    }

    if (st.restricted.length) {
      h.push('<ul class="vl-cards">');
      st.restricted.forEach(function (n) {
        var isNew = st.added.indexOf(n) >= 0;
        h.push("<li>" + cardLink(n, isNew ? "vl-new" : "") + "</li>");
      });
      h.push("</ul>");
    } else {
      h.push("<p><em>Nothing restricted at this point.</em></p>");
    }

    h.push('<div class="vl-count">Banned</div>');
    h.push('<p class="vl-banned">' + (st.banned.length
      ? st.banned.map(function (n) { return cardLink(n); }).join(" · ")
      : "<em>No individually banned cards yet.</em>") + "</p>");

    var cats = CATS.filter(function (c) {
      return !c.since || c.since <= ev.date;
    });
    if (cats.length) {
      h.push('<details class="vl-cats"><summary>' + cats.length +
             " category ban" + (cats.length === 1 ? "" : "s") +
             " also in force</summary><ul>");
      cats.forEach(function (c) {
        h.push("<li><strong>" + esc(c.name) + "</strong>" +
               (c.count ? " (" + c.count + ")" : "") + " — " +
               esc(c.rule || "") + "</li>");
      });
      h.push("</ul></details>");
    }

    var q = poolQuery(ev, st);
    h.push('<a class="vl-pool" target="_blank" rel="noopener noreferrer" href="' +
           "https://scryfall.com/search?q=" + encodeURIComponent(q) +
           '">Legal card pool on Scryfall →</a>');

    // provenance, including where the sources disagree
    var disputes = ev.actions.filter(function (a) { return a.disagree; });
    if (disputes.length) {
      h.push('<div class="vl-dispute"><strong>Sources disagree on this date.</strong>');
      disputes.forEach(function (a) {
        var claims = Object.keys(a.claims || {}).sort().map(function (k) {
          return (SOURCES[k] ? SOURCES[k].title : k) + ": " + a.claims[k];
        }).join(" · ");
        h.push("<div>" + esc(a.card) + " (" + esc(a.action) + ") — " +
               esc(claims) + ". Using " +
               esc(SOURCES[a.from] ? SOURCES[a.from].title : a.from) + ".</div>");
      });
      h.push("</div>");
    }
    if (ev.sources && ev.sources.length) {
      h.push('<p class="vl-src">Source: ' + ev.sources.map(function (u) {
        return '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer">' +
               esc(u.replace(/^https?:\/\//, "").split("/")[0]) + "</a>";
      }).join(", ") + "</p>");
    }

    stateEl.innerHTML = h.join("");

    var bar = document.getElementById("vl-bar");
    if (bar) {
      bar.textContent = prettyDate(ev) + " · " + st.restricted.length +
                        " restricted";
    }
  }

  // ---- per-card history ---------------------------------------------------
  function historyOf(name) {
    var rows = [];
    EVENTS.forEach(function (ev) {
      ev.actions.forEach(function (a) {
        if (a.card === name) rows.push({ ev: ev, action: a.action });
      });
    });
    return rows;
  }

  var modal = document.getElementById("vl-hist");
  var modalBox = document.getElementById("vl-hist-box");

  function openHistory(name) {
    var rows = historyOf(name);
    var info = CARDS[name] || {};
    var h = ['<button class="vl-hist-close" aria-label="Close">×</button>'];
    h.push("<h3>" + esc(name) + "</h3>");
    if (info.set_name) {
      h.push("<p>" + esc(info.type_line || "") +
             (info.mana_cost ? " · " + esc(info.mana_cost) : "") +
             "<br>First printed in <strong>" + esc(info.set_name) +
             "</strong> (" + esc(info.set || "") + ")" +
             (info.released_at ? ", " + esc(info.released_at) : "") + "</p>");
    }
    h.push("<table><tbody>");
    rows.forEach(function (r) {
      h.push("<tr><td>" + esc(prettyDate(r.ev)) + "</td><td><strong>" +
             esc(r.action) + "</strong></td><td style=\"opacity:.65\">" +
             esc(r.ev.basis === "unknown" ? "basis unrecorded" : r.ev.basis) +
             "</td></tr>");
    });
    h.push("</tbody></table>");
    h.push("<p style=\"font-size:.85em;opacity:.7\">" + rows.length +
           " action" + (rows.length === 1 ? "" : "s") + " on record.</p>");
    if (info.scryfall_uri) {
      h.push('<p><a href="' + esc(info.scryfall_uri) +
             '" target="_blank" rel="noopener noreferrer">View on Scryfall →</a></p>');
    }
    modalBox.innerHTML = h.join("");
    modal.classList.add("is-open");
  }

  function closeHistory() { modal.classList.remove("is-open"); }

  document.addEventListener("click", function (e) {
    var hist = e.target.closest && e.target.closest(".vl-hist-open");
    if (hist) {
      e.preventDefault();
      openHistory(hist.dataset.card);
      return;
    }
    if (e.target.closest && e.target.closest(".vl-hist-close")) {
      closeHistory(); return;
    }
    if (modal && e.target === modal) closeHistory();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") closeHistory();
  });

  // ---- scroll driving -----------------------------------------------------
  var buttons = Array.prototype.slice.call(
    document.querySelectorAll(".vl-ev"));
  var currentIdx = -1;

  function setCurrent(i, pushHash) {
    if (i === currentIdx) return;
    currentIdx = i;
    buttons.forEach(function (b, n) {
      b.classList.toggle("is-current", n === i);
    });
    render(i);
    if (pushHash && history.replaceState) {
      history.replaceState(null, "", "#" + EVENTS[i].date);
    }
  }

  if ("IntersectionObserver" in window) {
    var io = new IntersectionObserver(function (entries) {
      // the entry nearest the top of the viewport wins
      var best = null;
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        if (!best || en.boundingClientRect.top < best.boundingClientRect.top) {
          best = en;
        }
      });
      if (best) {
        var i = buttons.indexOf(best.target);
        if (i >= 0) setCurrent(i, true);
      }
    }, { rootMargin: "-20% 0px -70% 0px", threshold: 0 });
    buttons.forEach(function (b) { io.observe(b); });
  }

  // clicking a rail entry selects it
  buttons.forEach(function (b, i) {
    b.addEventListener("click", function () { setCurrent(i, true); });
  });

  // ---- deep link ----------------------------------------------------------
  function fromHash() {
    var h = (location.hash || "").replace(/^#/, "");
    if (!h) return -1;
    for (var i = 0; i < EVENTS.length; i++) {
      if (EVENTS[i].date === h) return i;
    }
    return -1;
  }

  var start = fromHash();
  if (start < 0) start = EVENTS.length - 1;   // default: the current list
  setCurrent(start, false);
  if (fromHash() >= 0 && buttons[start]) {
    buttons[start].scrollIntoView({ block: "center" });
  }
  window.addEventListener("hashchange", function () {
    var i = fromHash();
    if (i >= 0) setCurrent(i, false);
  });

  // mobile: tapping the summary bar jumps to the state panel
  var bar = document.getElementById("vl-bar");
  if (bar) {
    bar.addEventListener("click", function () {
      stateEl.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  }

  var ns = document.querySelector(".vl-noscript");
  if (ns) ns.remove();
})();
