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
  var details = document.getElementById("vl-details");
  if (!dataEl || !panel) return;

  var DATA = JSON.parse(dataEl.textContent);
  var EVENTS = DATA.events.slice().sort(function (a, b) { return a.seq - b.seq; });
  var CARDS = DATA.cards || {};
  var CATS = DATA.categories || [];
  var POOL = DATA.pool_exclusions || [];
  var SOURCES = DATA.sources || {};
  var ERAS = DATA.eras || [];
  var KINDS = DATA.change_kinds || {};
  var ERA_BY_NO = {};
  ERAS.forEach(function (e) { ERA_BY_NO[e.era] = e; });

  // Eras between one announcement and the next. Not every change to the
  // format is a B&R action: errata, rules changes and new sets move it too,
  // and they are often why the next announcement happened at all.
  function erasBetween(idx, ev) {
    // walk back to the most recent announcement that HAS an era; using the
    // immediately preceding one drags in eras from 1994 whenever it has none
    var lo = 0;
    for (var k = idx - 1; k >= 0; k--) {
      if (EVENTS[k].era) { lo = EVENTS[k].era; break; }
    }
    var hi = ev.era;
    if (!hi) return [];
    return ERAS.filter(function (e) {
      // must RECORD a change. Without this an era with no changes text fell
      // back to its own name, so "Time Vault Wars" -- the name of era 61 --
      // was listed as though something called that had happened.
      if (!e.changes || !e.changes.trim()) return false;
      return e.era > (lo || 0) && e.era < hi &&
             (e.change_kinds || []).some(function (k) {
               return k !== "set_release";
             });
    });
  }

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
  // We now have both dates from the chart, so say so rather than hedging.
  // A tournament held between them used the OLD list.
  function basisNote(ev) {
    var bits = [];
    if (ev.announced && ev.announced !== ev.effective) {
      bits.push("announced " + prettyISO(ev.announced) +
                ", took effect " + prettyISO(ev.effective));
    } else if (ev.announced) {
      bits.push("announced and effective the same day");
    } else {
      bits.push("effective date; announcement date not recorded");
    }
    if (ev.precision === "month") bits.push("exact day unknown");
    else if (ev.precision === "year") bits.push("month and day unknown");
    return bits.join(" \u00b7 ");
  }

  function prettyISO(d) {
    if (!d) return "";
    var p = d.split("-");
    if (p.length < 3) return d;
    return MONTHS[+p[1] - 1] + " " + (+p[2]) + ", " + p[0];
  }

  // ---- replay -------------------------------------------------------------
  var STATES = [];
  (function () {
    var restricted = [], banned = [];
    // When a card last entered each lid. A card thrown in later must lie on
    // top of the pile: you cannot toss a card into a box and have it slide
    // underneath the ones already there. A card that leaves and comes back
    // gets a new, higher entry, so it lands back on top.
    var enteredR = {}, enteredB = {};
    EVENTS.forEach(function (ev) {
      // deltas are tracked for BOTH halves of the list: a card moving from
      // restricted to banned has to show as leaving one and joining the other
      var added = [], removed = [], bAdded = [], bRemoved = [];
      ev.actions.forEach(function (a) {
        var ri = restricted.indexOf(a.card), bi = banned.indexOf(a.card);
        if (a.action === "restrict") {
          if (ri < 0) {
            restricted.push(a.card); added.push(a.card);
            enteredR[a.card] = ev.seq;
          }
          if (bi >= 0) { banned.splice(bi, 1); bRemoved.push(a.card); }
        } else if (a.action === "unrestrict") {
          if (ri >= 0) { restricted.splice(ri, 1); removed.push(a.card); }
        } else if (a.action === "ban") {
          if (bi < 0) {
            banned.push(a.card); bAdded.push(a.card);
            enteredB[a.card] = ev.seq;
          }
          if (ri >= 0) { restricted.splice(ri, 1); removed.push(a.card); }
        } else if (a.action === "unban") {
          if (bi >= 0) { banned.splice(bi, 1); bRemoved.push(a.card); }
        }
      });
      STATES.push({ restricted: restricted.slice().sort(cmp),
                    banned: banned.slice().sort(cmp),
                    added: added.sort(cmp), removed: removed.sort(cmp),
                    bAdded: bAdded.sort(cmp), bRemoved: bRemoved.sort(cmp),
                    enteredR: Object.assign({}, enteredR),
                    enteredB: Object.assign({}, enteredB) });
    });
  })();

  var MAXN = STATES.reduce(function (m, s) {
    return Math.max(m, s.restricted.length); }, 0);

  // ---- chart --------------------------------------------------------------
  var svg = document.getElementById("vl-chart");
  var W = 900, H = 250, PAD_L = 30, PAD_R = 10, PAD_T = 12, PAD_B = 62;
  // the band under the axis holds one tick row per action kind
  var TICK_ROWS = ["restrict", "unrestrict", "ban", "unban"];
  var TICK_H = 9;
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

    // Action ticks, one row per kind, directly under the axis. These were a
    // separate vis-timeline widget, which meant two stacked controls with
    // different drag behaviour -- drag-to-scrub here, drag-to-pan there. Same
    // information, one control.
    var rowsUsed = TICK_ROWS.filter(function (act) {
      return EVENTS.some(function (ev) {
        return ev.actions.some(function (a) { return a.action === act; });
      });
    });
    rowsUsed.forEach(function (act, r) {
      var y = sy(0) + 10 + r * TICK_H;
      var lab = el("text", { class: "vl-axis-text", x: PAD_L - 5, y: y + 4,
                             "text-anchor": "end", "font-size": "7" });
      lab.textContent = { restrict: "restr", unrestrict: "unrestr",
                          ban: "ban", unban: "unban" }[act];
      svg.appendChild(lab);
      EVENTS.forEach(function (ev, i) {
        var n = ev.actions.filter(function (a) { return a.action === act; }).length;
        if (!n) return;
        var x = sx(asYear(ev.date));
        var t = el("rect", {
          class: "vl-tick vl-tick-" + act,
          x: x - 1.6, y: y - 3, width: 3.2,
          height: Math.min(7, 3 + n * 0.5), rx: 1 });
        t.appendChild(el("title")).textContent =
          prettyDate(ev) + " \u2014 " + n + " " + act +
          (n === 1 ? "" : (act.slice(-1) === "n" ? "ned" : "d"));
        svg.appendChild(t);
      });
    });

    // playhead
    headLine = el("line", { class: "vl-head", y1: PAD_T - 6,
                            y2: sy(0) + 10 + rowsUsed.length * TICK_H });
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
  // Both halves of the B&R list are rendered as card art, every step. Cards
  // this announcement ADDED get a green ring and glow; cards it REMOVED stay
  // in place for one step, greyed out under a red cross, so you can see them
  // go rather than having them silently vanish.
  //
  // Scryfall's "small" image is ~13 KB against ~140 KB for "normal": 98 cards
  // is about 1.3 MB in total, and the URLs are identical from step to step so
  // the browser caches them after the first pass.
  function smallArt(name) {
    var info = CARDS[name] || {};
    var u = info.image || "";
    return u ? u.replace("/normal/", "/small/") : "";
  }

  // ---- shoebox view ------------------------------------------------------
  // Two lids, one for banned and one for restricted, with the cards thrown in
  // face up. Scatter is DETERMINISTIC -- derived from a hash of the card name
  // -- so a card always lands in the same spot and the pile does not reshuffle
  // every time you move a step.
  function hash32(str) {
    var h = 2166136261;
    for (var i = 0; i < str.length; i++) {
      h ^= str.charCodeAt(i);
      h = (h * 16777619) >>> 0;
    }
    return h;
  }
  // three independent 0..1 values from one name
  function jitter(name) {
    var h = hash32(name);
    return [((h & 0x3ff) / 1023),
            (((h >>> 10) & 0x3ff) / 1023),
            (((h >>> 20) & 0x3ff) / 1023)];
  }

  // Each lid has a FIXED height, sized once for the largest the list ever
  // gets, so the box does not grow and shrink as you step through. Early
  // announcements leave it sparse, which is the right trade.
  // Each lid gets a stable SLOT for every card that ever appears in it.
  // Pure hash placement kept a card still but clumped the pile: the banned
  // lid had nineteen cards piled on top of each other with half the box
  // empty. A slot per card spreads them evenly and still never moves one.
  function rosterOf(pick) {
    var all = {};
    STATES.forEach(function (st) {
      pick(st).forEach(function (n) { all[n] = 1; });
    });
    return Object.keys(all).sort(cmp);
  }

  var ROSTER = {
    restricted: rosterOf(function (st) {
      return st.restricted.concat(st.removed); }),
    banned: rosterOf(function (st) {
      return st.banned.concat(st.bRemoved); })
  };
  var SLOT = { restricted: {}, banned: {} };
  Object.keys(ROSTER).forEach(function (k) {
    ROSTER[k].forEach(function (n, i) { SLOT[k][n] = i; });
  });

  // Each lid gives every card that ever appears in it a stable SLOT. Placing
  // by hash alone kept a card still but clumped the pile -- the banned lid had
  // nineteen cards heaped in one corner with half the box empty. A slot per
  // card spreads them across the lid and still never moves one.
  function rosterOf(pick) {
    var all = {};
    STATES.forEach(function (st) {
      pick(st).forEach(function (n) { all[n] = 1; });
    });
    return Object.keys(all).sort(cmp);
  }
  var ROSTER = {
    restricted: rosterOf(function (st) {
      return st.restricted.concat(st.removed); }),
    banned: rosterOf(function (st) {
      return st.banned.concat(st.bRemoved); })
  };
  var SLOT = { restricted: {}, banned: {} };
  Object.keys(ROSTER).forEach(function (k) {
    ROSTER[k].forEach(function (n, i) { SLOT[k][n] = i; });
  });

  var LID_H = (function () {
    function maxOf(pick) {
      return STATES.reduce(function (m, st) {
        return Math.max(m, pick(st).length); }, 0);
    }
    // sized for the whole roster, not the current count, so the box never
    // changes size as you step through
    function layout(n) {
      var cols = Math.max(6, Math.ceil(Math.sqrt(Math.max(n, 1) * 2.6)));
      var rows = Math.ceil(Math.max(n, 1) / cols);
      return { cols: cols, rows: rows,
               h: Math.max(150, rows * 46 + 64) };
    }
    return {
      restricted: layout(ROSTER.restricted.length),
      banned: layout(ROSTER.banned.length)
    };
  })();

  // A lid contains its cards: none may sit on or over the rim. The lid's
  // border IS the lip, so cards are kept inside the box within it.
  //
  // The maths is done on the UNTRANSFORMED layout box (offsetLeft/offsetWidth)
  // and the rotated extent derived from it, rather than on
  // getBoundingClientRect. A card that is being thrown in is mid-animation
  // when this runs, so its measured box is wherever the animation currently
  // has it -- which is how The Fantasticar kept landing outside the lid.
  function containCards(root) {
    (root || document).querySelectorAll(".vl-lid").forEach(function (lid) {
      var innerW = lid.clientWidth;
      var innerH = lid.clientHeight;
      if (!innerW || !innerH) return;
      var pad = 4;                        // clearance from the lip

      lid.querySelectorAll(".vl-thrown").forEach(function (card) {
        var w = card.offsetWidth;
        if (!w) return;
        // Height is DERIVED from the width, not read from the element. The
        // art is lazy-loaded, so before it arrives the card has no laid-out
        // height, and reading offsetHeight skipped those cards entirely --
        // they then sat outside the lid for good. Cards are a known shape.
        var h = w * (204 / 146);
        var rot = parseFloat(
          (card.style.getPropertyValue("--rot") || "0").replace("deg", "")) || 0;
        var rad = Math.abs(rot * Math.PI / 180);
        var c = Math.abs(Math.cos(rad)), si = Math.abs(Math.sin(rad));
        var bw = w * c + h * si;          // rotated bounding box
        var bh = h * c + w * si;
        // a card being pulled out lifts upward; it must not lift over the rim
        var lift = card.classList.contains("is-gone") ? 36 : 0;

        var cx = card.offsetLeft + w / 2;
        var cy = card.offsetTop + h / 2;
        var minX = pad + bw / 2, maxX = innerW - pad - bw / 2;
        var minY = pad + bh / 2 + lift, maxY = innerH - pad - bh / 2;
        var nx = bw >= innerW - 2 * pad ? innerW / 2
                                        : Math.max(minX, Math.min(cx, maxX));
        var ny = bh + lift >= innerH - 2 * pad ? innerH / 2 + lift / 2
                                               : Math.max(minY, Math.min(cy, maxY));
        if (Math.abs(nx - cx) < 0.5 && Math.abs(ny - cy) < 0.5) return;
        card.style.left = (((nx - w / 2) / innerW) * 100).toFixed(2) + "%";
        card.style.top = (ny - h / 2).toFixed(0) + "px";
      });
    });
  }

  function shoeboxHtml(current, removed, added, label, id, kind, entered) {
    var shown = current.slice();
    removed.forEach(function (n) { shown.push(n); });
    shown.sort(cmp);

    var lay = LID_H[kind], slots = SLOT[kind];
    var lidH = lay.h, cols = lay.cols, rows = lay.rows;
    var cardW = 8.5;                         // percent of lid width
    var cellW = (100 - 2) / cols;
    var cellH = (lidH - 34 - 14) / Math.max(rows, 1);

    var out = ['<div class="vl-lid" id="' + id +
               '" style="height:' + lidH + 'px">'];
    out.push('<span class="vl-lid-label">' + esc(label) + " \u00b7 " +
             current.length + "</span>");
    shown.forEach(function (name) {
      var gone = current.indexOf(name) < 0;
      var isNew = added.indexOf(name) >= 0;
      // the slot holds the card in one place; the hash only tilts it and
      // nudges it off the grid, so it reads as a heap rather than a table
      var slot = slots[name] || 0;
      var j = jitter(name);
      var col = slot % cols, row = Math.floor(slot / cols);
      var left = 1 + col * cellW + (j[0] - 0.5) * cellW * 0.5;
      left = Math.max(0.5, Math.min(100 - cardW - 0.5, left));
      var top = 30 + row * cellH + (j[1] - 0.5) * cellH * 0.35;
      var rot = (j[2] - 0.5) * 40;
      var cls = "vl-thrown" + (gone ? " is-gone" : isNew ? " is-add" : "");
      var art = smallArt(name);
      out.push('<a href="#" class="' + cls + ' autocard vl-hist-open"' +
               ' data-card="' + esc(name) + '" title="' + esc(name) + '"' +
               ' style="left:' + left.toFixed(2) + "%;top:" + top.toFixed(0) +
               "px;width:" + cardW + "%;--rot:" + rot.toFixed(1) + "deg;z-index:" +
               (gone ? 9000 : 100 + ((entered && entered[name]) || 0)) + '">' +
               (art ? '<img src="' + esc(art) + '" alt="' + esc(name) +
                      '" loading="lazy">'
                    : '<span class="vl-noart">' + esc(name) + "</span>") +
               (gone ? '<span class="vl-thrown-x" aria-hidden="true">\u2715</span>' : "") +
               "</a>");
    });
    if (!shown.length) {
      out.push('<p class="vl-lid-empty"><em>empty</em></p>');
    }
    out.push("</div>");
    return out.join("");
  }

  function gridHtml(current, removed, added, id) {
    var shown = current.slice();
    removed.forEach(function (n) { shown.push(n); });
    shown.sort(cmp);
    if (!shown.length) return "";
    var out = ['<ul class="vl-grid" id="' + id + '">'];
    shown.forEach(function (n) {
      var gone = current.indexOf(n) < 0;
      var isNew = added.indexOf(n) >= 0;
      var cls = gone ? "is-gone" : (isNew ? "is-add" : "");
      var art = smallArt(n);
      out.push('<li class="vl-cell ' + cls + '" data-card="' + esc(n) + '">');
      out.push('<a href="#" class="autocard vl-hist-open" data-card="' +
               esc(n) + '" title="' + esc(n) + '">');
      out.push(art
        ? '<img src="' + esc(art) + '" alt="' + esc(n) +
          '" loading="lazy" width="146" height="204">'
        : '<span class="vl-noart">' + esc(n) + "</span>");
      out.push('<span class="vl-cell-name">' + esc(n) + "</span>");
      out.push("</a></li>");
    });
    out.push("</ul>");
    return out.join("");
  }


  var VIEW = "grid";
  try { VIEW = localStorage.getItem("vl-view") || "grid"; } catch (e) { /* private mode */ }

  function render(i) {
    var ev = EVENTS[i], st = STATES[i];

    var h = [], d = [];
    h.push('<div class="vl-head-row">');
    h.push('<span class="vl-asof-n">' + st.restricted.length +
           "<small>restricted</small></span>");
    h.push("<h2 class=\"vl-asof\">" + esc(prettyDate(ev)) + "</h2>");
    // era and dates sit out to the right of the heading rather than stacking
    // under it, which made the header tall and the column ragged
    h.push('<div class="vl-head-meta">');
    h.push('<p class="vl-era">' + (ev.era_name
      ? "Era " + ev.era + " \u00b7 " + esc(ev.era_name)
      : "\u00a0") + "</p>");
    h.push('<p class="vl-basis">' + esc(basisNote(ev)) +
           " \u00b7 announcement " + ev.seq + " of " + EVENTS.length + "</p>");
    h.push("</div>");
    h.push("</div>");

    // The summary is rendered AFTER the grids, further down: it wraps to one
    // or two lines depending on the announcement, and above the grid that
    // shifted every card down a row as you stepped through.
    var chg = [];
    st.added.forEach(function (n) { chg.push('<span class="vl-chg-a">+ ' + esc(n) + "</span>"); });
    st.removed.forEach(function (n) { chg.push('<span class="vl-chg-r">\u2212 ' + esc(n) + "</span>"); });
    st.bAdded.forEach(function (n) { chg.push('<span class="vl-chg-r">banned ' + esc(n) + "</span>"); });
    st.bRemoved.forEach(function (n) { chg.push('<span class="vl-chg-a">unbanned ' + esc(n) + "</span>"); });

    if (VIEW === "shoebox") {
      h.push(shoeboxHtml(st.restricted, st.removed, st.added,
                         "Restricted", "vl-list", "restricted", st.enteredR));
    } else {
      h.push('<div class="vl-sec">Restricted \u2014 one copy allowed <span class="vl-sec-n">'
             + st.restricted.length + "</span></div>");
      h.push(gridHtml(st.restricted, st.removed, st.added, "vl-list") ||
             "<p><em>Nothing restricted yet.</em></p>");
    }

    if (VIEW === "shoebox") {
      h.push(shoeboxHtml(st.banned, st.bRemoved, st.bAdded,
                         "Banned", "vl-banned-list", "banned", st.enteredB));
    } else {
      h.push('<div class="vl-sec">Banned \u2014 not allowed at all <span class="vl-sec-n">'
             + st.banned.length + "</span></div>");
      h.push(gridHtml(st.banned, st.bRemoved, st.bAdded, "vl-banned-list") ||
             "<p><em>No individually banned cards yet.</em></p>");
    }

    // The link and the citation are fixed height, so they go FIRST: below
    // the class bans and the change list they moved on every step, because
    // those vary in length.
    d.push('<a class="vl-pool" target="_blank" rel="noopener noreferrer" href="' +
           "https://scryfall.com/search?q=" +
           encodeURIComponent(poolQuery(ev, st)) +
           '"><i class="fa fa-magnifying-glass" aria-hidden="true"></i> Legal card pool on this date</a>');

    // what happened in the format between the last announcement and this one
    var between = erasBetween(i, ev);
    if (between.length) {
      d.push('<div class="vl-sec">Since the last announcement</div>');
      d.push('<ul class="vl-between">');
      between.forEach(function (e) {
        var tags = (e.change_kinds || [])
          .filter(function (k) { return k !== "set_release"; })
          .map(function (k) {
            return '<span class="vl-kind vl-kind-' + esc(k) + '" title="' +
                   esc(KINDS[k] || k) + '">' + esc(k.replace("_", " ")) +
                   "</span>";
          }).join(" ");
        d.push("<li>" + tags + " " + esc(e.changes) +
               (e.citation && e.citation.url
                 ? ' <a href="' + esc(e.citation.url) + '" target="_blank" ' +
                   'rel="noopener noreferrer">source</a>' +
                   (e.citation.archived
                     ? ' <a href="' + esc(e.citation.archived) +
                       '" target="_blank" rel="noopener noreferrer">(archived)</a>'
                     : "")
                 : "") + "</li>");
      });
      d.push("</ul>");
    }

    var ann = ev.announcement;
    if (ann && ann.url) {
      d.push('<p class="vl-src"><strong>Announcement:</strong> ' +
             '<a href="' + esc(ann.url) + '" target="_blank" ' +
             'rel="noopener noreferrer">' + esc(ann.label || ann.url) + "</a>" +
             (ann.archived
               ? ' \u00b7 <a href="' + esc(ann.archived) + '" target="_blank" ' +
                 'rel="noopener noreferrer">archived copy</a>'
               : ' \u00b7 <span class="vl-noarchive">no archived copy</span>') +
             "</p>");
    } else if (ev.sources && ev.sources.length) {
      d.push('<p class="vl-src">Source: ' + ev.sources.map(function (u) {
        return '<a href="' + esc(u) + '" target="_blank" rel="noopener noreferrer">' +
               esc(u.replace(/^https?:\/\//, "").split("/")[0]) + "</a>";
      }).join(", ") + "</p>");
    }


    // Everything from here is detail rather than the list itself, and it
    // goes in the left column under the controls, which was otherwise empty
    // while the right column ran long with the cards.
    // Class bans are part of the banned list, so they are shown, not hidden
    // behind a toggle.
    var cats = CATS.filter(function (c) { return c.since && c.since <= ev.date; });
    if (cats.length) {
      d.push('<ul class="vl-classban">');
      cats.forEach(function (c) {
        d.push('<li><span class="vl-classban-n">' +
               (c.count ? c.count : "all") + "</span> <strong>" +
               esc(c.name) + "</strong> \u2014 " + esc(c.rule || "") + "</li>");
      });
      d.push("</ul>");
    }

    d.push('<div class="vl-sec">What this announcement changed</div>');
    d.push('<p class="vl-chg">' + (chg.length ? chg.join(" ") :
           '<em class="vl-nochange">No change to the list.</em>') + "</p>");

    var pools = POOL.filter(function (p) { return !p.since || p.since <= ev.date; });
    if (pools.length) {
      d.push('<details class="vl-pool-note"><summary>' + pools.length +
             " kind" + (pools.length === 1 ? "" : "s") +
             " of card outside the pool entirely</summary><ul>");
      pools.forEach(function (p) {
        d.push("<li><strong>" + esc(p.name) + "</strong> — " +
               esc(p.note || "") + "</li>");
      });
      d.push("</ul><p style=\"opacity:.7\">These were never tournament legal, " +
             "so no B&amp;R action ever applied to them.</p></details>");
    }

    panel.innerHTML = h.join("");
    if (details) details.innerHTML = d.join("");
    containCards(panel);

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
    railSelect(i, true);
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

  var viewBtn = document.getElementById("vl-view");
  function paintViewBtn() {
    if (!viewBtn) return;
    viewBtn.textContent = VIEW === "shoebox" ? "\u25a6 Grid view"
                                             : "\ud83d\udce6 Shoebox view";
    viewBtn.setAttribute("aria-pressed", VIEW === "shoebox" ? "true" : "false");
  }
  if (viewBtn) {
    paintViewBtn();
    viewBtn.addEventListener("click", function () {
      VIEW = VIEW === "shoebox" ? "grid" : "shoebox";
      try { localStorage.setItem("vl-view", VIEW); } catch (e) { /* private mode */ }
      paintViewBtn();
      render(idx);
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

    // ONE ITEM PER (ANNOUNCEMENT, ACTION), not per card. 149 card-level items
    // stacked into an unreadable scroll and clipped their own labels at the
    // window edge; aggregating gives ~60 items that sit on one row each, and
    // the cards go in the tooltip where there is room for them.
    var LABEL = { restrict: "restricted", unrestrict: "unrestricted",
                  ban: "banned", unban: "unbanned" };
    var items = [], used = {};
    EVENTS.forEach(function (ev, i) {
      var byAction = {};
      ev.actions.forEach(function (a) {
        (byAction[a.action] = byAction[a.action] || []).push(a.card);
      });
      Object.keys(byAction).forEach(function (act) {
        var cards = byAction[act].slice().sort(cmp);
        used[act] = 1;
        items.push({
          id: i + ":" + act,
          group: act,
          start: asDate(ev.date),
          content: cards.length === 1 ? cards[0] : cards.length + " cards",
          className: "vl-i-" + act,
          title: prettyDate(ev) + " \u2014 " + cards.length + " " +
                 LABEL[act] + ":\n" + cards.join("\n")
        });
      });
    });

    var groups = [
      { id: "restrict",   content: "restricted" },
      { id: "unrestrict", content: "unrestricted" },
      { id: "ban",        content: "banned" },
      { id: "unban",      content: "unbanned" }
    ].filter(function (g) { return used[g.id]; });

    // leave a margin either side so labels near 1994 and 2026 are not clipped
    var first = asDate(EVENTS[0].date);
    var last = asDate(EVENTS[EVENTS.length - 1].date);
    var pad = (last - first) * 0.06;

    try {
      timeline = new vis.Timeline(host, new vis.DataSet(items),
                                  new vis.DataSet(groups), {
        stack: false,
        min: new Date(first.getTime() - pad * 2),
        max: new Date(last.getTime() + pad * 2),
        start: new Date(first.getTime() - pad),
        end: new Date(last.getTime() + pad),
        zoomMin: 1000 * 60 * 60 * 24 * 120,
        zoomMax: 1000 * 60 * 60 * 24 * 365 * 45,
        orientation: { axis: "bottom" },
        margin: { item: { horizontal: 2, vertical: 6 } },
        selectable: true,
        horizontalScroll: true,
        zoomKey: "ctrlKey",
        tooltip: { followMouse: true, overflowMethod: "cap" }
      });
      timeline.on("select", function (p) {
        if (!p.items || !p.items.length) return;
        stop();
        select(+String(p.items[0]).split(":")[0], true);
      });
      var fb = document.querySelector(".vl-rail-fallback");
      if (fb) fb.remove();
    } catch (err) {
      // the chart and scrubber stand alone
    }
  }

  // Highlight the selected announcement on the rail and, if it has scrolled
  // out of view, pan to it. Panning only -- the zoom level is the reader's,
  // so following the playhead must not undo their zoom.
  function railSelect(i, follow) {
    if (!timeline) return;
    var ids = [];
    ["restrict", "unrestrict", "ban", "unban"].forEach(function (act) {
      if (EVENTS[i].actions.some(function (a) { return a.action === act; })) {
        ids.push(i + ":" + act);
      }
    });
    try { timeline.setSelection(ids, { focus: false }); } catch (e) { /* cosmetic */ }
    if (follow === false) return;
    try {
      var when = asDate(EVENTS[i].date).getTime();
      var win = timeline.getWindow();
      var a = win.start.getTime(), b = win.end.getTime();
      var inset = (b - a) * 0.12;          // treat the edges as "out of view"
      if (when < a + inset || when > b - inset) {
        timeline.moveTo(when, { animation: { duration: 420,
                                             easingFunction: "easeInOutQuad" } });
      }
    } catch (e) { /* panning is a nicety */ }
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

  // The rail is a secondary, optional view. Building it inside a closed
  // <details> gives a zero-height layout, so it is built on first open.
  var railWrap = document.getElementById("vl-rail-wrap");
  if (railWrap) {
    railWrap.addEventListener("toggle", function () {
      if (!railWrap.open) return;
      if (!timeline) { buildRail(); }
      railSelect(idx, false);
      if (timeline) {
        try { timeline.redraw(); } catch (e) { /* layout is best-effort */ }
      }
    });
  }

  // a narrower lid can leave a card outside, so re-clamp when the box changes
  var resizeTimer = null;
  window.addEventListener("resize", function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function () { containCards(panel); }, 120);
  });
  // belt and braces: clamp again once the art has actually arrived
  window.addEventListener("load", function () { containCards(panel); });

  var ns = document.querySelector(".vl-noscript");
  if (ns) ns.remove();
})();
