// Shared Scryfall image lookup for the two card-hover paths on this site.
//
// decklist.js fills a preview pane beside a decklist; autocard.js floats a
// tooltip for <<Card Name>> links in prose. Both were calling Scryfall directly
// and both had the same three problems:
//
//   - no caching. Scryfall's API guidelines ask that results be cached, and a
//     decklist page here carries thousands of card links -- a single event
//     report has 332 -- so running the cursor down one fired a request per link.
//   - data.data[0].image_uris read unconditionally. A double-faced card has no
//     image_uris at all (they live on card_faces[]), so hovering one threw.
//   - no guard on an empty result. A misspelled or renamed card name makes
//     data.data empty, so data.data[0] is undefined and hovering threw.
//
// window.TSCards.image(name, mode) resolves to an image url, or null. It never
// rejects: a card that cannot be resolved simply has no preview, and the link
// still works.
window.TSCards = (function () {
  "use strict";

  var KEY = "ts-card-img-v1";
  var mem = {};
  var inflight = {};

  try {
    mem = JSON.parse(localStorage.getItem(KEY) || "{}");
  } catch (e) {
    mem = {};
  }

  function remember(k, url) {
    mem[k] = url;
    try {
      localStorage.setItem(KEY, JSON.stringify(mem));
    } catch (e) {
      /* quota, or private browsing: the in-memory cache still applies */
    }
  }

  function pick(card) {
    if (!card) return null;
    if (card.image_uris && card.image_uris.normal) return card.image_uris.normal;
    // Double-faced, split and transforming cards carry images per face.
    if (card.card_faces) {
      for (var i = 0; i < card.card_faces.length; i++) {
        var f = card.card_faces[i];
        if (f.image_uris && f.image_uris.normal) return f.image_uris.normal;
      }
    }
    return null;
  }

  // mode "original" keeps decklist.js's behaviour of preferring the first
  // printing, which is what you want for old school. mode "exact" is a plain
  // name lookup, which is what autocard.js wants.
  function url(name, mode) {
    return mode === "original"
      ? 'https://api.scryfall.com/cards/search?q=!"' + encodeURIComponent(name) + '"+not%3Areprint'
      : "https://api.scryfall.com/cards/named?exact=" + encodeURIComponent(name);
  }

  function image(name, mode) {
    if (!name) return Promise.resolve(null);
    var k = (mode || "exact") + "|" + name;

    if (Object.prototype.hasOwnProperty.call(mem, k)) {
      return Promise.resolve(mem[k]);
    }
    if (inflight[k]) return inflight[k];

    inflight[k] = fetch(url(name, mode))
      .then(function (r) {
        if (!r.ok) return null;           // 404 for an unknown name is normal
        return r.json();
      })
      .then(function (data) {
        if (!data) return null;
        // /search returns a list; /named returns the card itself.
        var card = data.data ? data.data[0] : data;
        var got = pick(card);
        remember(k, got);                  // cache misses too, so we ask once
        return got;
      })
      .catch(function () {
        return null;                       // offline or blocked: no preview
      })
      .then(function (got) {
        delete inflight[k];
        return got;
      });

    return inflight[k];
  }

  return { image: image, pick: pick };
})();
