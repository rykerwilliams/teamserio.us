require "cgi"
require 'uri'

module Jekyll
  class DeckfileTag < Liquid::Tag
    def initialize(tag_name, text, tokens)
      super
      @file_path = text.strip
    end

    def render(context)
      site = context.registers[:site]
      base = site.source  # root of Jekyll project
      full_path = File.join(base, @file_path)
      title = File.basename(@file_path, ".txt")  # e.g. "mydeck"

      unless File.exist?(full_path)
        return "<p><em>Decklist file not found: #{@file_path}</em></p>"
      end

      decklist_html = ""
      decklist_txt  = ""

      decklist = File.read(full_path).strip
      decklist.split("\n").each do |line|
        if line.strip.downcase.start_with?("sideboard") || line.strip.empty?
          decklist_html += "<strong>Sideboard</strong><br>"
          decklist_txt  += "\n"
        else
          decklist_html += process_line(line)
          decklist_txt  += line + "\n" unless line.empty?
        end
      end

      newdecklist = decklist_txt.gsub("'", "&#39;")

      # Ensure file path is web-accessible (strip site source)
      rel_path = @file_path.sub(/^#{Regexp.escape(site.source)}\//, "")
      # The tag argument may or may not be written with a leading slash, and
      # both spellings are in use across the posts. Concatenating "/" onto a
      # path that already had one produced href="//assets/files/...", which a
      # browser reads as PROTOCOL-relative: it resolves to https://assets/...,
      # a host that does not exist, so every download button on that post was
      # dead. Normalise to exactly one leading slash.
      href_path = "/" + rel_path.sub(%r{\A/+}, "")

      <<~HTML
        <div class="decklist-content">
          <div class="decklist-title">#{title}</div>
          <div class="decklist-actions">
            <button onclick="copyDecklist(this)" class="btn btn-sm decklist-copy-btn">
              <i class="far fa-copy"></i> Copy
            </button>
            <a href="#{href_path}" download class="btn btn-sm decklist-download-btn">
              <i class="fas fa-download"></i> MTGO
            </a>
          </div>
          <div class="card-preview"></div>
          <div class="copyable-decklist"><pre>#{newdecklist}</pre></div>
          <div class="display-decklist">#{decklist_html}</div>
        </div>
      HTML
    end

    private

    def process_line(line)
        if line =~ /^(\d+)\s+(.*)$/
          quantity = $1
          card_name = $2.strip
          card_url = "https://scryfall.com/search?q=#{URI.encode_www_form_component(card_name)}"
          # data-cardname carries the card's REAL name. It used to be
        # form-encoded, which the hover code then passed to Scryfall verbatim
        # (and encodeURIComponent'd a second time) -- so "Swords to Plowshares"
        # went out as "Swords+to+Plowshares" and 404'd. Only single-word cards
        # resolved, which is why most previews were blank but a few worked.
        # The href stays URL-encoded; that one really is a URL.
        card_html = "<a href='#{card_url}' class='card-link' data-cardname=\"#{CGI.escapeHTML(card_name)}\" target='_blank'>#{card_name}</a>"
          "#{quantity} #{card_html}<br>"
        else
          # Handle lines that don't match the quantity pattern
          card_name = line.strip
          if card_name.empty?
            ""
          else
            card_url = "https://scryfall.com/search?q=#{URI.encode_www_form_component(card_name)}"
            "<a href='#{card_url}' class='card-link' data-cardname=\"#{CGI.escapeHTML(card_name)}\" target='_blank'>#{card_name}</a><br>"
          end
        end
      end
  end
end

Liquid::Template.register_tag('deckfile', Jekyll::DeckfileTag)
