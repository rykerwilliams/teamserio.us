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

      doc.content = transform(doc.content)
    end

    # Match <<Card Name>> OR ((Card Name))
    CARD = /(?:<<(.+?)>>|\(\((.+?)\)\))/

    # Regions that must never be rewritten. The output_ext guard above only keeps
    # the plugin away from assets that render to .js -- it does nothing for an
    # HTML page that *contains* JavaScript, and that is the dangerous case.
    #
    # On digitalmeh.net the search page contains
    #     var out = esc((from ? '...' : '') + text.slice(from, to) ...)
    # and the ((...)) pattern turned that into an <a> tag mid-expression, so the
    # page became a syntax error and search silently stopped working on the live
    # site. Nothing here triggers it today; this is so nothing has to.
    SKIP = %r{(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|
               <pre\b[^>]*>.*?</pre>|<code\b[^>]*>.*?</code>)}mix

    def transform(content)
      content.split(SKIP).map do |part|
        part =~ /\A<(script|style|pre|code)\b/im ? part : rewrite(part)
      end.join
    end

    def rewrite(text)
      text.gsub(CARD) do
        card = (Regexp.last_match(1) || Regexp.last_match(2)).strip
        %Q{<a href="https://scryfall.com/card?q=#{CGI.escape(card)}" class="autocard" data-card="#{card}">#{card}</a>}
      end
    end
  end
end
