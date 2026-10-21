// /vintage-decklists -- what the Vintage championship Top 8s played.
//
// Two charts over one slice of the data, chosen by the filter row: the most
// played cards (share of Top 8 lists that play each, or total copies), and one card's share
// year by year, with the years it was restricted shaded. A list counts once
// per card however many copies it plays, so a restricted card and a 4-of are
// measured the same way: how many of the best decks wanted it. The copies
// view answers the other question -- how much of the Top 8s' cardboard it was
// -- where a 4-of like Force of Will outweighs every restricted card.
//
// Everything below the charts on the page is plain HTML; this only adds the
// charts, and the section stays hidden if it never runs.
(function () {
  "use strict";

  var me = document.currentScript;
  var SRC = me.getAttribute("data-src");
  var BASE = me.getAttribute("data-base");
  var SVGNS = "http://www.w3.org/2000/svg";
  var TOP_N = 25;

  // labels in the data -> the series a reader filters by
  var SERIES = [
    { key: "early", name: "Before 2003",
      labels: ["Worlds", "AndCon", "Pro Tour Dallas", "Beyond Dominia"] },
    { key: "gencon", name: "Gen Con", labels: ["Gen Con", "Magic Weekend Chicago"] },
    { key: "na", name: "EW North America", labels: ["Eternal Weekend NA"] },
    { key: "eu", name: "EW Europe", labels: ["Eternal Weekend Europe"] },
    { key: "asia", name: "EW Asia", labels: ["Eternal Weekend Asia"] },
    { key: "online", name: "EW Online", labels: ["Eternal Weekend Online"] }
  ];
  var seriesOf = {};
  SERIES.forEach(function (s) { s.labels.forEach(function (l) { seriesOf[l] = s.key; }); });

  var D, CARDS, byName = {};
  var state = { series: {}, from: null, to: null, side: false, card: null,
                measure: "lists" };
  var tip = document.getElementById("vd-tip");

  function el(tag, attrs, parent) {
    var n = document.createElementNS(SVGNS, tag);
    for (var k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function text(tag, attrs, str, parent) {
    var n = el(tag, attrs, parent);
    n.textContent = str;
    return n;
  }
  function pct(x) { return Math.round(x * 100) + "%"; }
  function year(ev) { return +ev.date.slice(0, 4); }

  // A bar with a 4px rounded data end and a square baseline. Horizontal bars
  // grow right from x0; columns grow up from y0.
  function hbar(x0, y, w, h) {
    var r = Math.min(4, w, h / 2);
    return "M" + x0 + "," + y + "h" + (w - r) + "a" + r + "," + r + " 0 0 1 " + r + "," + r +
           "v" + (h - 2 * r) + "a" + r + "," + r + " 0 0 1 " + (-r) + "," + r + "h" + (r - w) + "z";
  }
  function vbar(x, y0, w, h) {
    var r = Math.min(4, h, w / 2);
    return "M" + x + "," + y0 + "v" + (r - h) + "a" + r + "," + r + " 0 0 1 " + r + "," + (-r) +
           "h" + (w - 2 * r) + "a" + r + "," + r + " 0 0 1 " + r + "," + r + "v" + (h - r) + "z";
  }

  // ---- tooltip --------------------------------------------------------------
  // Lines of [strong value, secondary label]; built with textContent, since
  // player and deck names are data.
  function showTip(evt, rows) {
    tip.textContent = "";
    rows.forEach(function (r) {
      var p = document.createElement("div");
      if (r[0]) {
        var b = document.createElement("strong");
        b.textContent = r[0];
        p.appendChild(b);
      }
      if (r[1]) p.appendChild(document.createTextNode((r[0] ? " " : "") + r[1]));
      tip.appendChild(p);
    });
    tip.hidden = false;
    var box = tip.parentNode.getBoundingClientRect();
    var x = evt.clientX - box.left + 14, y = evt.clientY - box.top + 14;
    if (x + tip.offsetWidth > box.width) x = Math.max(0, x - tip.offsetWidth - 28);
    tip.style.left = x + "px";
    tip.style.top = y + "px";
  }
  function hideTip() { tip.hidden = true; }
  function hover(node, rows) {
    node.addEventListener("pointermove", function (e) { showTip(e, rows()); });
    node.addEventListener("pointerleave", hideTip);
    node.addEventListener("focus", function () {
      var r = node.getBoundingClientRect();
      showTip({ clientX: r.right, clientY: r.top }, rows());
    });
    node.addEventListener("blur", hideTip);
  }

  // ---- the slice --------------------------------------------------------------
  function inSeries(ev) { return state.series[seriesOf[ev.label]]; }
  function events() {
    return D.events.filter(function (ev) {
      var y = year(ev);
      return inSeries(ev) && y >= state.from && y <= state.to;
    });
  }
  // the keys a list plays, once each, and how many copies
  function plays(deck) {
    var out = {};
    var parts = state.side ? [deck.main, deck.sideboard] : [deck.main];
    parts.forEach(function (p) {
      (p || []).forEach(function (c) { out[c[1]] = (out[c[1]] || 0) + c[0]; });
    });
    return out;
  }
  function lists(evs) {
    var out = [];
    evs.forEach(function (ev) {
      ev.decks.forEach(function (d, i) { if (d.main) out.push({ ev: ev, deck: d, i: i }); });
    });
    return out;
  }

  // ---- most played ------------------------------------------------------------
  function drawTop() {
    var ls = lists(events());
    var tally = {};
    ls.forEach(function (l) {
      var p = plays(l.deck);
      for (var k in p) {
        var t = tally[k] || (tally[k] = { key: k, lists: 0, copies: 0 });
        t.lists += 1;
        t.copies += p[k];
      }
    });
    var rows = Object.keys(tally).map(function (k) { return tally[k]; })
      .sort(function (a, b) {
        var m = state.measure, o = m === "lists" ? "copies" : "lists";
        return b[m] - a[m] || b[o] - a[o] ||
               CARDS[a.key].name.localeCompare(CARDS[b.key].name);
      });
    var copies = state.measure === "copies";

    var nev = events().length;
    document.getElementById("vd-top-hint").textContent = ls.length
      ? (copies ? "Total copies of each card across the "
                : "Share of the ") + ls.length + " Top 8 lists from " + nev +
        (nev === 1 ? " event" : " events") + (copies ? "" : " that play each card") +
        (state.side ? ", main deck and sideboard" : ", main deck only") +
        (copies ? ". A restricted card counts at most one per list." : ".") +
        " Click a card to see it year by year."
      : "No lists match these filters.";

    var svg = document.getElementById("vd-top");
    svg.textContent = "";
    var top = rows.slice(0, TOP_N);
    var W = svg.parentNode.clientWidth || 700;
    var LABEL = Math.min(210, W * 0.42), VAL = 44, ROW = 24, BAR = 14;
    var H = Math.max(1, top.length) * ROW + 4;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("height", H);
    var span = W - LABEL - VAL;
    // the bar's length: a share of lists, or copies against the leader
    var most = top.length ? top[0].copies : 1;
    function size(r) { return copies ? r.copies / most : r.lists / ls.length; }
    function label(r) { return copies ? String(r.copies) : pct(r.lists / ls.length); }
    // 0, half and full scale: enough to read a bar's length against
    [0, 0.5, 1].forEach(function (f) {
      el("line", { x1: LABEL + f * span, x2: LABEL + f * span, y1: 0, y2: H,
                   "class": "vd-grid" }, svg);
    });
    top.forEach(function (r, i) {
      var share = r.lists / ls.length, len = size(r), y = i * ROW;
      var g = el("g", { "class": "vd-row" + (r.key === state.card ? " is-on" : ""),
                        tabindex: 0, role: "button",
                        "aria-label": CARDS[r.key].name + ", " + label(r) +
                                      (copies ? " copies" : "") }, svg);
      el("rect", { x: 0, y: y, width: W, height: ROW, "class": "vd-hit" }, g);
      text("text", { x: LABEL - 8, y: y + ROW / 2, "class": "vd-label",
                     "text-anchor": "end", "dominant-baseline": "central" },
           CARDS[r.key].name, g);
      el("path", { d: hbar(LABEL, y + (ROW - BAR) / 2, Math.max(1, len * span), BAR),
                   "class": "vd-bar" }, g);
      text("text", { x: LABEL + len * span + 6, y: y + ROW / 2, "class": "vd-value",
                     "dominant-baseline": "central" }, label(r), g);
      hover(g, function () {
        var a = [String(r.copies), "copies in all"],
            b = [pct(share), "of lists (" + r.lists + " of " + ls.length + ")"];
        var avg = (r.copies / r.lists).toFixed(1).replace(/\.0$/, "");
        return [copies ? a : b, copies ? b : a, [avg, "per list that plays it"],
                ["", CARDS[r.key].name]];
      });
      function pick() { selectCard(r.key, true); }
      g.addEventListener("click", pick);
      g.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") { e.preventDefault(); pick(); }
      });
    });

    var tb = document.querySelector("#vd-top-table tbody");
    tb.textContent = "";
    rows.slice(0, 100).forEach(function (r) {
      var tr = document.createElement("tr");
      [CARDS[r.key].name, r.lists, pct(r.lists / ls.length), r.copies].forEach(function (v, j) {
        var td = document.createElement("td");
        td.textContent = v;
        if (j) td.className = "vd-num";
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
  }

  // ---- one card by year ---------------------------------------------------------
  // Every year the chosen series held a championship, ignoring the year
  // filter: the point of this chart is the whole arc.
  function drawYear() {
    var svg = document.getElementById("vd-year");
    svg.textContent = "";
    var hint = document.getElementById("vd-year-hint");
    var title = document.getElementById("vd-card-title");
    var list = document.getElementById("vd-card-lists");
    if (list) list.remove();
    if (!state.card) {
      title.textContent = "One card over the years";
      hint.textContent = "Pick a card to see how much of each year's Top 8s played it.";
      svg.setAttribute("height", 0);
      return;
    }
    var key = state.card, name = CARDS[key].name;
    title.textContent = name + " over the years";

    var years = {};
    D.events.forEach(function (ev) {
      if (!inSeries(ev)) return;
      var y = years[year(ev)] || (years[year(ev)] = { year: year(ev), lists: 0, with: 0,
                                                       restricted: false, evs: [] });
      y.evs.push(ev);
      if ((ev.restricted || []).indexOf(key) >= 0) y.restricted = true;
      ev.decks.forEach(function (d) {
        if (!d.main) return;
        y.lists += 1;
        if (plays(d)[key]) y.with += 1;
      });
    });
    var ys = Object.keys(years).map(function (k) { return years[k]; })
      .filter(function (y) { return y.lists; })
      .sort(function (a, b) { return a.year - b.year; });
    var anyR = ys.some(function (y) { return y.restricted; });
    hint.textContent = "Share of each year's Top 8 lists that play " + name +
      (state.side ? " (main deck or sideboard)" : " in the main deck") + "." +
      (anyR ? " Shaded years: restricted at that year's championship." : "");

    var W = svg.parentNode.clientWidth || 700, H = 220, PADL = 36, PADB = 22, PADT = 18;
    svg.setAttribute("viewBox", "0 0 " + W + " " + H);
    svg.setAttribute("height", H);
    var plotH = H - PADB - PADT, band = (W - PADL) / Math.max(1, ys.length);
    var colW = Math.max(2, Math.min(24, band - 2));
    [0, 0.5, 1].forEach(function (f) {
      var y = PADT + plotH * (1 - f);
      el("line", { x1: PADL, x2: W, y1: y, y2: y, "class": f ? "vd-grid" : "vd-axis" }, svg);
      text("text", { x: PADL - 6, y: y, "class": "vd-tick", "text-anchor": "end",
                     "dominant-baseline": "central" }, pct(f), svg);
    });
    var peak = ys.reduce(function (m, y) {
      return y.with / y.lists > (m ? m.with / m.lists : -1) ? y : m;
    }, null);
    var every = Math.ceil(ys.length / Math.max(1, Math.floor((W - PADL) / 38)));
    ys.forEach(function (y, i) {
      var share = y.with / y.lists, x = PADL + i * band;
      var g = el("g", { "class": "vd-col", tabindex: 0,
                        "aria-label": y.year + ": " + pct(share) }, svg);
      el("rect", { x: x, y: 0, width: band, height: H, "class": y.restricted ? "vd-rband" : "vd-hit" }, g);
      if (share > 0) {
        el("path", { d: vbar(x + (band - colW) / 2, PADT + plotH, colW, Math.max(1, share * plotH)),
                     "class": "vd-bar" }, g);
      }
      if (y === peak && share > 0) {
        text("text", { x: x + band / 2, y: PADT + plotH * (1 - share) - 5, "class": "vd-value",
                       "text-anchor": "middle" }, pct(share), g);
      }
      if (i % every === 0 || i === ys.length - 1) {
        text("text", { x: x + band / 2, y: H - 6, "class": "vd-tick", "text-anchor": "middle" },
             "'" + String(y.year).slice(2), g);
      }
      hover(g, function () {
        var rows = [[pct(share), "of " + y.year + "'s lists"],
                    [y.with + " of " + y.lists, "lists"]];
        if (y.restricted) rows.push(["", "Restricted"]);
        y.evs.forEach(function (ev) { rows.push(["", ev.label]); });
        return rows;
      });
    });

    // and the lists themselves, linked
    var hits = [];
    lists(D.events.filter(inSeries)).forEach(function (l) {
      var n = plays(l.deck)[key];
      if (n) hits.push({ l: l, n: n });
    });
    var det = document.createElement("details");
    det.id = "vd-card-lists";
    det.className = "vd-table-wrap";
    var sum = document.createElement("summary");
    sum.textContent = "The " + hits.length + " lists that play " + name;
    det.appendChild(sum);
    var ul = document.createElement("ul");
    ul.className = "vd-hits";
    hits.reverse().forEach(function (h) {
      var li = document.createElement("li");
      var a = document.createElement("a");
      a.href = BASE + h.l.ev.slug + "/#deck-" + (h.l.i + 1);
      a.textContent = h.l.deck.player;
      li.appendChild(document.createTextNode(h.l.ev.date.slice(0, 4) + " " + h.l.ev.label + ", " +
                                             h.l.deck.finish + ": "));
      li.appendChild(a);
      li.appendChild(document.createTextNode(" — " + (h.l.deck.archetype || "") +
                                             (h.n > 1 ? " (" + h.n + ")" : "")));
      ul.appendChild(li);
    });
    det.appendChild(ul);
    svg.parentNode.insertBefore(det, svg.nextSibling);
  }

  function selectCard(key, scroll) {
    state.card = key;
    document.getElementById("vd-card").value = key ? CARDS[key].name : "";
    if (history.replaceState) {
      history.replaceState(null, "", key ? "#card=" + encodeURIComponent(CARDS[key].name)
                                         : location.pathname);
    }
    drawTop();
    drawYear();
    if (scroll) document.getElementById("vd-card-title").scrollIntoView({ behavior: "smooth" });
  }

  function redraw() { hideTip(); drawTop(); drawYear(); }

  // ---- filters ----------------------------------------------------------------
  function setup() {
    var chips = document.getElementById("vd-series");
    SERIES.forEach(function (s) {
      state.series[s.key] = true;
      var b = document.createElement("button");
      b.type = "button";
      b.className = "vd-chip";
      b.textContent = s.name;
      b.setAttribute("aria-pressed", "true");
      b.addEventListener("click", function () {
        state.series[s.key] = !state.series[s.key];
        b.setAttribute("aria-pressed", String(state.series[s.key]));
        redraw();
      });
      chips.appendChild(b);
    });

    var yrs = D.events.map(year), lo = Math.min.apply(null, yrs), hi = Math.max.apply(null, yrs);
    var from = document.getElementById("vd-from"), to = document.getElementById("vd-to");
    for (var y = lo; y <= hi; y++) {
      from.appendChild(new Option(y, y));
      to.appendChild(new Option(y, y));
    }
    state.from = lo; state.to = hi;
    from.value = lo; to.value = hi;
    function range(e) {
      state.from = +from.value; state.to = +to.value;
      if (state.from > state.to) {   // keep the range the right way round
        if (e.target === from) { state.to = state.from; to.value = state.to; }
        else { state.from = state.to; from.value = state.from; }
      }
      redraw();
    }
    from.addEventListener("change", range);
    to.addEventListener("change", range);
    var measures = document.querySelectorAll("#vd-measure button");
    Array.prototype.forEach.call(measures, function (b) {
      b.addEventListener("click", function () {
        state.measure = b.getAttribute("data-measure");
        Array.prototype.forEach.call(measures, function (o) {
          o.setAttribute("aria-pressed", String(o === b));
        });
        redraw();
      });
    });
    document.getElementById("vd-side").addEventListener("change", function (e) {
      state.side = e.target.checked;
      redraw();
    });

    var dl = document.getElementById("vd-card-names");
    Object.keys(byName).sort().forEach(function (n) {
      var o = document.createElement("option");
      o.value = n;
      dl.appendChild(o);
    });
    var input = document.getElementById("vd-card");
    input.addEventListener("input", function () {
      var k = byName[input.value];
      if (k && k !== state.card) selectCard(k, false);
    });

    var m = /^#card=(.+)$/.exec(location.hash);
    if (m) state.card = byName[decodeURIComponent(m[1])] || null;
    if (state.card) input.value = CARDS[state.card].name;

    var t;
    window.addEventListener("resize", function () { clearTimeout(t); t = setTimeout(redraw, 150); });
  }

  fetch(SRC).then(function (r) { return r.json(); }).then(function (data) {
    D = data;
    CARDS = data.cards;
    for (var k in CARDS) byName[CARDS[k].name] = k;
    document.getElementById("vd-charts").hidden = false;
    setup();
    redraw();
  }).catch(function () { /* the charts stay hidden; the table below still works */ });
})();
