# _plugins/mtg_autocard.rb
require "cgi"

module Jekyll
  class MTGAutocard < Jekyll::Generator
    def generate(site)
      (site.posts.docs + site.pages).each { |doc| replace_cards(doc) }
    end

    def replace_cards(doc)
      return unless doc.content

      # Match <<Card Name>> OR ((Card Name))
      doc.content = doc.content.gsub(/(?:<<(.+?)>>|\(\((.+?)\)\))/) do
        card = Regexp.last_match(1) || Regexp.last_match(2)
        card.strip!
        %Q{<a href="https://scryfall.com/card?q=#{CGI.escape(card)}" class="autocard" data-card="#{card}">#{card}</a>}
      end
    end
  end
end
