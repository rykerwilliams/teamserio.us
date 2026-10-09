# _plugins/mtg_autocard.rb
require "cgi"

module Jekyll
  class MTGAutocard < Jekyll::Generator
    def generate(site)
      (site.posts.docs + site.pages).each { |doc| replace_cards(doc) }
    end

    def replace_cards(doc)
      return unless doc.content
      # Only rewrite documents that render to HTML.
      #
      # site.pages includes every theme asset carrying front matter, so without
      # this the card pattern also matches JavaScript. chulapa 2.x's search
      # script contains arrow functions like
      #     .map(([key, indices]) => ({ ... }))
      # whose doubled parentheses look exactly like ((Card Name)), and an <a>
      # tag injected mid-expression makes the file a syntax error - search dies
      # with "Unexpected identifier 'href'". The 1.x search script happened not
      # to contain that shape, so this stayed hidden.
      return unless doc.respond_to?(:output_ext) && doc.output_ext == '.html'

      # Match <<Card Name>> OR ((Card Name))
      doc.content = doc.content.gsub(/(?:<<(.+?)>>|\(\((.+?)\)\))/) do
        card = Regexp.last_match(1) || Regexp.last_match(2)
        card.strip!
        %Q{<a href="https://scryfall.com/card?q=#{CGI.escape(card)}" class="autocard" data-card="#{card}">#{card}</a>}
      end
    end
  end
end
