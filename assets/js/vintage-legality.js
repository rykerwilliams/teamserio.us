// /vintage-legality -- the Vintage B&R list on any date since 1994.
//
// Three linked controls over one replay of the event list:
//   1. an area chart of how many cards were restricted over time, which also
//      acts as the scrubber (drag it, or press Play to walk 32 years)
//   2. a zoomable vis-timeline rail of every action
//   3. the state panel, with card art for whatever the announcement changed
//
// The <noscript> block in the page carries the full record, so none of this is
// load-bearing for reading the data.
(function () {
  "use strict";

  var dataEl = document.getElementById("vl-data");
  var panel = document.getElementById("vl-state");
  if (!dataEl || !panel) return;

  var DATA = JSON.parse(dataEl.textContent);
  var EVENTS = DATA.events.slice().sort(function (a, b) { return a.seq - b.seq; });
  var CARDS = DATA.cards || {};
  var CATS = DATA.categories || [];
  var POOL = DATA.pool_exclusions || [];
  var SOURCES = DATA.sources || {};

  function cmp(a, b) { return a.localeCompare(b); }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;",
               '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---- dates --------------------------------------------------------------
  var MONTHS = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"];

  function parts(d) { return d.split("-").map(Number); }

  // a partial date as a fractional year, for plotting
  function asYear(d) {
    var p = parts(d);
    return p[0] + ((p[1] || 6) - 1) / 12 + ((p[2] || 15) - 1) / 365;
  }
  // a partial date as a real Date, for vis-timeline
  function asDate(d) {
    var p = parts(d);
    return new Date(Date.UTC(p[0], (p[1] || 6) - 1, p[2] || 15));
  }
  function prettyDate(ev) {
    var p = parts(ev.date);
    if (ev.precision === "day") return MONTHS[p[1] - 1] + " " + p[2] + ", " + p[0];
    if (ev.precision === "month") return MONTHS[p[1] - 1] + " " + p[0];
    return String(p[0]);
  }
  // Say plainly what the date is and is not: most announcements do not record
  // whether their date is the announcement or the effective date, and a
  // tournament held between the two used the OLD list.
  function basisNote(ev) {
    var b = [];
    if (ev.basis === "effective") b.push("effective date");
    else if (ev.basis === "announced") b.push("announcement date");
    else b.push("date basis unrecorded — may be announcement or effective");
    if (ev.precision === "month") b.push("exact day unknown");
    else if (ev.precision === "year") b.push("month and day unknown");
    return b.join(" · ");
  }

  // ---- replay -------------------------------------------------------------
  var STATES = [];
  (function () {
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
      STATES.push({ restricted: restricted.slice().sort(cmp),
                    banned: banned.slice().sort(cmp),
                    added: added.sort(cmp), removed: removed.sort(cmp) });
    });
  })();

  var MAXN = STATES.reduce(function (m, s) {
    return Math.max(m, s.restricted.length); }, 0);

  // ---- chart --------------------------------------------------------------
  var svg = document.getElementById("vl-chart");
  var W = 900, H = 210, PAD_L = 30, PAD_R = 10, PAD_T = 12, PAD_B = 24;
  var X0 = asYear(EVENTS[0].date), X1 = asYear(EVENTS[EVENTS.length - 1].date);

  function sx(year) {
    return PAD_L + (year - X0) / (X1 - X0) * (W - PAD_L - PAD_R);
  }
  function sy(n) {
    return H - PAD_B - (n / MAXN) * (H - PAD_T - PAD_B);
  }
  function el(name, attrs) {
    var e = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.keys(attrs || {}).forEach(function (k) {
      e.setAttribute(k, attrs[k]);
    });
    return e;
  }

  var headLine, headDot;

  function drawChart() {
    if (!svg) return;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("role", "img");
    svg.setAttribute("aria-label",
      "Number of cards restricted in Vintage over time, " +
      EVENTS[0].date + " to " + EVENTS[EVENTS.length - 1].date);

    // horizontal gridlines + y labels
    [0, 13, 26, 39, 52].forEach(function (n) {
      if (n > MAXN) return;
      svg.appendChild(el("line", { class: "vl-grid", x1: PAD_L, x2: W - PAD_R,
                                   y1: sy(n), y2: sy(n) }));
      var t = el("text", { class: "vl-axis-text", x: PAD_L - 5, y: sy(n) + 3,
                           "text-anchor": "end" });
      t.textContent = n;
      svg.appendChild(t);
    });

    // the count is a step function: it holds until the next announcement
    var dPts = [], aPts = [];
    EVENTS.forEach(function (ev, i) {
      var x = sx(asYear(ev.date)), y = sy(STATES[i].restricted.length);
      var prevY = i ? sy(STATES[i - 1].restricted.length) : sy(0);
      dPts.push((i ? "L" : "M") + x + " " + prevY, "L" + x + " " + y);
      aPts.push("L" + x + " " + prevY, "L" + x + " " + y);
    });
    var lastX = sx(X1), lastY = sy(STATES[STATES.length - 1].restricted.length);
    dPts.push("L" + lastX + " " + lastY);
    aPts.push("L" + lastX + " " + lastY);

    svg.appendChild(el("path", {
      class: "vl-area",
      d: "M" + PAD_L + " " + sy(0) + aPts.join(" ") +
         " L" + lastX + " " + sy(0) + " Z" }));
    svg.appendChild(el("path", { class: "vl-line", d: dPts.join(" ") }));

    // x axis with decade ticks
    svg.appendChild(el("line", { class: "vl-axis", x1: PAD_L, x2: W - PAD_R,
                                 y1: sy(0), y2: sy(0) }));
    for (var y = 1995; y <= 2026; y += 5) {
      var xx = sx(y);
      svg.appendChild(el("line", { class: "vl-axis", x1: xx, x2: xx,
                                   y1: sy(0), y2: sy(0) + 4 }));
      var lab = el("text", { class: "vl-axis-text", x: xx, y: H - 8,
                             "text-anchor": "middle" });
      lab.textContent = "’" + String(y).slice(2);
      svg.appendChild(lab);
    }

    // playhead
    headLine = el("line", { class: "vl-head", y1: PAD_T - 6, y2: sy(0) });
    headDot = el("circle", { class: "vl-head-dot", r: 5 });
    svg.appendChild(headLine);
    svg.appendChild(headDot);

    // one invisible hit target per announcement, for clicking precisely
    EVENTS.forEach(function (ev, i) {
      var c = el("circle", { class: "vl-pt", r: 4,
                             cx: sx(asYear(ev.date)),
                             cy: sy(STATES[i].restricted.length) });
      c.addEventListener("click", function (e) {
        e.stopPropagation(); stop(); select(i, true);
      });
      svg.appendChild(c);
    });
  }

  function moveHead(i) {
    if (!headLine) return;
    var x = sx(asYear(EVENTS[i].date));
    headLine.setAttribute("x1", x);
    headLine.setAttribute("x2", x);
    headDot.setAttribute("cx", x);
    headDot.setAttribute("cy", sy(STATES[i].restricted.length));
  }

  // nearest announcement to an x position in SVG user units
  function nearestTo(xUser) {
    var best = 0, bestD = Infinity;
    EVENTS.forEach(function (ev, i) {
      var d = Math.abs(sx(asYear(ev.date)) - xUser);
      if (d < bestD) { bestD = d; best = i; }
    });
    return best;
  }

  function svgX(clientX) {
    var r = svg.getBoundingClientRect();
    return (clientX - r.left) / r.width * W;
  }

  // ---- card art -----------------------------------------------------------
  // Only the cards an announcement touched get art: that is where the interest
  // is, and it keeps this to a few images per step rather than fifty.
  function artFigure(name, kind) {
    var fig = document.createElement("figure");
    fig.className = "vl-dcard " + (kind === "add" ? "is-add" : "is-rem");
    var img = document.createElement("img");
    img.alt = name;
    img.loading = "lazy";
    img.width = 146; img.height = 204;
    var info = CARDS[name] || {};
    // prefer the original printing we already recorded; fall back to the
    // shared cache, which also prefers first printings
    if (info.image) {
      img.src = info.image;
    } else if (window.TSCards && window.TSCards.image) {
      window.TSCards.image(name, "original").then(function (u) {
        if (u) img.src = u;
      });
    }
    var cap = document.createElement("figcaption");
    var tag = document.createElement("span");
    tag.className = "vl-dtag";
    tag.textContent = kind === "add" ? "restricted" : "no longer";
    var a = document.createElement("a");
    a.href = "#";
    a.className = "autocard vl-hist-open";
    a.dataset.card = name;
    a.textContent = name;
    cap.appendChild(tag);
    cap.appendChild(a);
    fig.appendChild(img);
    fig.appendChild(cap);
    return fig;
  }

  // ---- Scryfall legal pool ------------------------------------------------
  // Excludes by NAME, never by is:ante -- Scryfall has no such filter and
  // silently ignores an unknown is: term, so that query quietly matches
  // everything while looking like it worked.
  function poolQuery(ev, st) {
    var c = parts(ev.date);
    var cutoff = c[0] + "-" + String(c[1] || 12).padStart(2, "0") + "-" +
                 String(c[2] || 28).padStart(2, "0");
    var terms = ["game:paper", "date<=" + cutoff, "-t:conspiracy"];
    POOL.forEach(function (p) {
      // an exclusion means nothing before the first set of its kind exists
      if (p.scryfall && (!p.since || p.since <= ev.date)) terms.push(p.scryfall);
    });
    var names = {};
    st.banned.forEach(function (n) { names[n] = 1; });
    CATS.forEach(function (cat) {
      if (!cat.cards || !cat.since || cat.since > ev.date) return;
      cat.cards.forEach(function (n) { names[n] = 1; });
    });
    Object.keys(names).sort(cmp).forEach(function (n) {
      terms.push('-!"' + n + '"');
    });
    return terms.join(" ");
  }

  // ---- render -------------------------------------------------------------
  var listEl = null;

  function render(i) {
    var ev = EVENTS[i], st = STATES[i];

    // measure the existing list so it can be FLIP-animated into its new order
    var before = {};
    if (listEl) {
      Array.prototype.forEach.call(listEl.children, function (li) {
        before[li.dataset.card] = li.getBoundingClientRect();
      });
    }

    var h = [];
    h.push('<div class="vl-head-row">');
    h.push('<span class="vl-asof-n">' + st.restricted.length +
           "<small>restricted</small></span>");
    h.push("<div><h2 class=\"vl-asof\">" + esc(prettyDate(ev)) + "</h2>");
    h.push('<p class="vl-basis">' + esc(basisNote(ev)) +
           " · announcement " + ev.seq + " of " + EVENTS.length + "</p></div>");
    h.push("</div>");

    if (st.added.length || st.removed.length) {
      h.push('<div class="vl-sec">What this announcement changed</div>');
      h.push('<div class="vl-delta" id="vl-delta"></div>');
    }

    h.push('<div class="vl-sec">Restricted — one copy allowed</div>');
    if (st.restricted.length) {
      h.push('<ul class="vl-cards" id="vl-list">');
      st.restricted.forEach(function (n) {
        h.push('<li data-card="' + esc(n) + '"' +
               (st.added.indexOf(n) >= 0 ? ' class="vl-new"' : "") + ">" +
               '<a href="#" class="autocard vl-hist-open" data-card="' +
               esc(n) + '">' + esc(n) + "</a></li>");
      });
      h.push("</ul>");
    } else {
      h.push("<p><em>Nothing restricted yet.</em></p>");
    }

    h.push('<div class="vl-sec">Banned outright</div>');
    h.push('<p class="vl-banned">' + (st.banned.length
      ? st.banned.map(function (n) {
          return '<a href="#" class="autocard vl-hist-open" data-card="' +
                 esc(n) + '">' + esc(n) + "</a>"; }).join(" · ")
      : "<em>No individually banned cards yet.</em>") + "</p>");

    var cats = CATS.filter(function (c) { return c.since && c.since <= ev.date; });
    if (cats.length) {
      h.push('<details class="vl-cats"><summary>' + cats.length +
             " class ban" + (cats.length === 1 ? "" : "s") +
             " also in force</summary><ul>");
      cats.forEach(function (c) {
        h.push("<li><strong>" + esc(c.name) + "</strong>" +
               (c.count ? " (" + c.count + ")" : "") + " — " +
               esc(c.rule || "") + "</li>");
      });
      h.push("</ul></details>");
    }

    var pools = POOL.filter(function (p) { return !p.since || p.since <= ev.date; });
    if (pools.length) {
      h.push('<details class="vl-pool-note"><summary>' + pools.length +
             " kind" + (pools.length === 1 ? "" : "s") +
             " of card outside the pool entirely</summary><ul>");
      pools.forEach(function (p) {
        h.push("<li><strong>" + esc(p.name) + "</strong> — " +
               esc(p.note || "") + "</li>");
      });
      h.push("</ul><p style=\"opacity:.7\">These were never tournament legal, " +
             "so no B&amp;R action ever applied to them.</p></details>");
    }

    h.push('<a class="vl-pool" target="_blank" rel="noopener noreferrer" href="' +
           "https://scryfall.com/search?q=" +
           encodeURIComponent(poolQuery(ev, st)) +
           '">Legal card pool on this date →</a>');

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

    panel.innerHTML = h.join("");

    var delta = document.getElementById("vl-delta");
    if (delta) {
      st.added.forEach(function (n) { delta.appendChild(artFigure(n, "add")); });
      st.removed.forEach(function (n) { delta.appendChild(artFigure(n, "rem")); });
    }

    // FLIP: play the list from where the old one was to where it is now
    listEl = document.getElementById("vl-list");
    if (listEl && Object.keys(before).length &&
        !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      Array.prototype.forEach.call(listEl.children, function (li) {
        var was = before[li.dataset.card];
        if (!was) return;
        var now = li.getBoundingClientRect();
        var dx = was.left - now.left, dy = was.top - now.top;
        if (!dx && !dy) return;
        li.style.transform = "translate(" + dx + "px," + dy + "px)";
        requestAnimationFrame(function () {
          li.classList.add("vl-flip");
          li.style.transform = "";
        });
      });
    }
  }

  // ---- per-card history ---------------------------------------------------
  var modal = document.getElementById("vl-hist");
  var modalBox = document.getElementById("vl-hist-box");

  function openHistory(name) {
    var rows = [];
    EVENTS.forEach(function (ev) {
      ev.actions.forEach(function (a) {
        if (a.card === name) rows.push({ ev: ev, action: a.action });
      });
    });
    var info = CARDS[name] || {};
    var h = ['<button class="vl-hist-close" aria-label="Close">×</button>'];
    if (info.image) {
      h.push('<img class="vl-hist-art" src="' + esc(info.image) +
             '" alt="" loading="lazy">');
    }
    h.push("<h3>" + esc(name) + "</h3>");
    h.push("<p>" + esc(info.type_line || "") +
           (info.mana_cost ? " · " + esc(info.mana_cost) : "") +
           (info.set_name ? "<br>First printed in <strong>" +
             esc(info.set_name) + "</strong>" +
             (info.released_at ? ", " + esc(info.released_at) : "") : "") +
           (info.total_paper_printings ? " · " + info.total_paper_printings +
             " paper printing" + (info.total_paper_printings === 1 ? "" : "s") : "") +
           "</p>");
    h.push("<table><tbody>");
    rows.forEach(function (r) {
      h.push("<tr><td>" + esc(prettyDate(r.ev)) + "</td><td><strong>" +
             esc(r.action) + "</strong></td><td style=\"opacity:.65\">" +
             esc(r.ev.basis === "unknown" ? "basis unrecorded" : r.ev.basis) +
             "</td></tr>");
    });
    h.push("</tbody></table>");
    h.push('<p style="font-size:.85em;opacity:.7">' + rows.length +
           " action" + (rows.length === 1 ? "" : "s") + " on record.</p>");
    if (info.scryfall_uri) {
      h.push('<p><a href="' + esc(info.scryfall_uri) +
             '" target="_blank" rel="noopener noreferrer">View on Scryfall →</a></p>');
    }
    modalBox.innerHTML = h.join("");
    modal.classList.add("is-open");
  }
  function closeHistory() { if (modal) modal.classList.remove("is-open"); }

  document.addEventListener("click", function (e) {
    var hit = e.target.closest && e.target.closest(".vl-hist-open");
    if (hit) { e.preventDefault(); openHistory(hit.dataset.card); return; }
    if (e.target.closest && e.target.closest(".vl-hist-close")) {
      closeHistory(); return;
    }
    if (modal && e.target === modal) closeHistory();
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") { closeHistory(); stop(); }
  });

  // ---- selection ----------------------------------------------------------
  var idx = -1, timeline = null;

  function select(i, pushHash) {
    i = Math.max(0, Math.min(EVENTS.length - 1, i));
    if (i === idx) return;
    idx = i;
    render(i);
    moveHead(i);
    var scrub = document.getElementById("vl-scrub");
    if (scrub && +scrub.value !== i) scrub.value = i;
    if (timeline) {
      try {
        timeline.setSelection(EVENTS[i].actions.map(function (_, k) {
          return i + ":" + k; }), { focus: false });
      } catch (err) { /* selection is cosmetic */ }
    }
    if (pushHash && history.replaceState) {
      history.replaceState(null, "", "#" + EVENTS[i].date);
    }
  }

  // ---- play ---------------------------------------------------------------
  var timer = null;
  var playBtn = document.getElementById("vl-play");

  function stop() {
    if (timer) { clearInterval(timer); timer = null; }
    if (playBtn) {
      playBtn.setAttribute("aria-pressed", "false");
      playBtn.textContent = "▶ Play";
    }
  }
  function play() {
    stop();
    if (idx >= EVENTS.length - 1) select(0, false);
    playBtn.setAttribute("aria-pressed", "true");
    playBtn.textContent = "❚❚ Pause";
    timer = setInterval(function () {
      if (idx >= EVENTS.length - 1) { stop(); return; }
      select(idx + 1, true);
    }, 1100);
  }
  if (playBtn) {
    playBtn.addEventListener("click", function () {
      timer ? stop() : play();
    });
  }

  // ---- chart dragging -----------------------------------------------------
  if (svg) {
    drawChart();
    var dragging = false;
    function fromPointer(e) {
      select(nearestTo(svgX(e.clientX)), true);
    }
    svg.addEventListener("pointerdown", function (e) {
      dragging = true; stop(); svg.setPointerCapture(e.pointerId);
      fromPointer(e);
    });
    svg.addEventListener("pointermove", function (e) {
      if (dragging) fromPointer(e);
    });
    svg.addEventListener("pointerup", function () { dragging = false; });
    svg.addEventListener("pointercancel", function () { dragging = false; });
  }

  // range input: keyboard-accessible equivalent of dragging the chart
  var scrub = document.getElementById("vl-scrub");
  if (scrub) {
    scrub.max = EVENTS.length - 1;
    scrub.addEventListener("input", function () {
      stop(); select(+scrub.value, true);
    });
  }

  // ---- vis-timeline rail --------------------------------------------------
  function buildRail() {
    var host = document.getElementById("vl-rail");
    if (!host || typeof vis === "undefined" || !vis.Timeline) return;
    var items = [], groups = [
      { id: "restrict",   content: "restricted" },
      { id: "unrestrict", content: "unrestricted" },
      { id: "ban",        content: "banned" },
      { id: "unban",      content: "unbanned" }
    ];
    var used = {};
    EVENTS.forEach(function (ev, i) {
      ev.actions.forEach(function (a, k) {
        used[a.action] = 1;
        items.push({
          id: i + ":" + k, group: a.action, start: asDate(ev.date),
          content: a.card, className: "vl-i-" + a.action,
          title: a.card + " — " + a.action + ", " + prettyDate(ev)
        });
      });
    });
    groups = groups.filter(function (g) { return used[g.id]; });
    try {
      timeline = new vis.Timeline(host, new vis.DataSet(items),
                                  new vis.DataSet(groups), {
        stack: true, stackSubgroups: true,
        min: asDate(EVENTS[0].date), max: new Date(Date.UTC(2027, 0, 1)),
        start: asDate(EVENTS[0].date), end: new Date(Date.UTC(2027, 0, 1)),
        zoomMin: 1000 * 60 * 60 * 24 * 60,
        maxHeight: 300, margin: { item: 3 }, selectable: true,
        tooltip: { followMouse: true }
      });
      timeline.on("select", function (p) {
        if (!p.items || !p.items.length) return;
        stop();
        select(+String(p.items[0]).split(":")[0], true);
      });
      var fb = document.querySelector(".vl-rail-fallback");
      if (fb) fb.remove();
    } catch (err) {
      // the chart and scrubber are enough on their own
    }
  }

  // ---- deep link ----------------------------------------------------------
  function fromHash() {
    var h = (location.hash || "").replace(/^#/, "");
    for (var i = 0; i < EVENTS.length; i++) {
      if (EVENTS[i].date === h) return i;
    }
    return -1;
  }
  window.addEventListener("hashchange", function () {
    var i = fromHash();
    if (i >= 0) { stop(); select(i, false); }
  });

  var start = fromHash();
  render(start < 0 ? EVENTS.length - 1 : start);
  idx = start < 0 ? EVENTS.length - 1 : start;
  moveHead(idx);
  if (scrub) scrub.value = idx;

  buildRail();
  if (timeline) {
    try {
      timeline.setSelection(EVENTS[idx].actions.map(function (_, k) {
        return idx + ":" + k; }), { focus: false });
    } catch (err) { /* cosmetic */ }
  }

  var ns = document.querySelector(".vl-noscript");
  if (ns) ns.remove();
})();
