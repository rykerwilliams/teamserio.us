require "cgi"
require "date"

# One page per championship at /vintage-decklists/<slug>/, from
# _data/vintage_t8.json (script/sync-vintage-t8.py). Rendered at build time so
# a list reads, copies and links with JavaScript off; the charts on the index
# page are the only part that needs it.
#
# The data keys each card line by a short oracle_id and keeps the card detail
# once in `cards`. Joining the two here, in Ruby, keeps the layout to plain
# loops instead of a lookup per card in Liquid.
module Jekyll
  class VintageT8Page < PageWithoutAFile
    def initialize(site, ev, prev_ev, next_ev, cards)
      super(site, site.source, File.join("vintage-decklists", ev["slug"]), "index.html")
      restricted = ev["restricted"] || []
      decks = ev["decks"].map do |d|
        d.merge(
          "main" => lines(d["main"], cards, restricted),
          "sideboard" => lines(d["sideboard"], cards, restricted),
          "main_count" => d["main"]&.sum { |c| c[0] },
          "sideboard_count" => d["sideboard"]&.sum { |c| c[0] },
          "text" => text(d, cards)
        )
      end
      data.merge!(
        "layout" => "vintage-t8-event",
        # read from the page, not the layout, by layouts/wide.html
        "header_type" => "none",
        "og_image" => "/assets/images/site/og-black-lotus.jpg",
        "title" => ev["event"],
        "subtitle" => [ev["label"], VintageT8Page.when(ev), ev["location"]].compact.join(" · "),
        "excerpt" => "Top 8 decklists from the #{ev["event"]} (#{ev["label"]}).",
        "event" => ev.merge("decks" => decks),
        "prev_event" => prev_ev && link(prev_ev),
        "next_event" => next_ev && link(next_ev),
        "show_breadcrumb" => true,
        "breadcrumb_list" => [
          { "label" => "Home", "url" => "/" },
          { "label" => "Vintage decklists", "url" => "/vintage-decklists/" }
        ]
      )
    end

    # The date as precisely as it is known -- never the placeholder day that
    # stands in for a range, a month or a year (decks/README.md in type1).
    def self.when(ev)
      d = Date.parse(ev["date"])
      case ev["date_precision"]
      when "year" then d.year.to_s
      when "month" then d.strftime("%B %Y")
      when "range"
        a = Date.parse(ev["date_range"][0])
        a.month == d.month ? "#{a.day}–#{d.strftime("%-d %B %Y")}" :
                             "#{a.strftime("%-d %B")} – #{d.strftime("%-d %B %Y")}"
      else d.strftime("%-d %B %Y")
      end
    end

    private

    def link(ev)
      { "url" => "/vintage-decklists/#{ev["slug"]}/", "title" => ev["event"],
        "label" => ev["label"] }
    end

    def lines(part, cards, restricted)
      return nil if part.nil?
      part.map do |count, key, printed_as|
        c = cards.fetch(key)
        name = c["name"]
        # a double-faced card the source named by its front face reads as
        # that face: "Delver of Secrets", not both faces and then the front
        if printed_as && name.start_with?("#{printed_as} // ")
          name, printed_as = printed_as, nil
        end
        { "count" => count, "name" => name, "printed_as" => printed_as,
          "image" => c["image"], "scryfall_uri" => c["scryfall_uri"],
          "set" => c["set"], "restricted" => restricted.include?(key) }
      end
    end

    # What the copy button puts on the clipboard: plain "4 Card Name" lines,
    # sideboard after a blank line, as every deck builder imports them.
    def text(d, cards)
      return nil if d["main"].nil?
      fmt = ->(part) { (part || []).map { |n, k, _| "#{n} #{cards.fetch(k)["name"]}" } }
      (fmt.(d["main"]) + (d["sideboard"] ? [""] + fmt.(d["sideboard"]) : [])).join("\n")
    end
  end

  class VintageT8Generator < Generator
    safe true

    def generate(site)
      t8 = site.data["vintage_t8"] or return
      evs = t8["events"]
      evs.each_with_index do |ev, i|
        site.pages << VintageT8Page.new(site, ev, i > 0 ? evs[i - 1] : nil,
                                        evs[i + 1], t8["cards"])
      end
      # the index page shows the same date strings without repeating the rule
      evs.each { |ev| ev["when"] = VintageT8Page.when(ev) }
      # what the B&R timeline needs to name the championships each list was
      # played under: a few KB, not the 800 KB of lists
      site.data["vintage_t8_summary"] = evs.map do |ev|
        w = ev["decks"].find { |d| d["finish"] == "1" }
        { "slug" => ev["slug"], "date" => ev["date"], "when" => ev["when"],
          "label" => ev["label"], "event" => ev["event"],
          "winner" => w && w["player"], "archetype" => w && w["archetype"] }
      end
    end
  end
end
