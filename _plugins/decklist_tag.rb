require 'uri'

module Jekyll
    class DecklistTag < Liquid::Block
      def initialize(tag_name, text, tokens)
        super
      end
  
      def render(context)
        decklist_html = ""
        decklist_txt = ""

        # Process each line of the decklist
        decklist = super.strip
        decklist.split("\n").each do |line|
          # Detect the word "Sideboard" and toggle flag
          if line.strip.downcase == "sideboard" or line.strip.downcase == 'sideboard:'
            decklist_html += "<strong>Sideboard</strong><br>"
            decklist_txt += "\n"
            @in_sideboard = true
          else
            decklist_html += process_line(line)
            if !line.empty?
              decklist_txt += line + "\n"
            end
          end
        end
        
        newdecklist = decklist_txt.gsub("'", "&#39;")
        
        # "<div class='decklist-content'><button onclick='copyDecklist(this)' class='btn text-muted btn-sm decklist-copy-btn'><i class='far fa-copy'></i></button><div class='card-preview'></div><pre class='decklist-content'><div class='copyable-decklist'>#{newdecklist}</div><div class='display-decklist'>#{decklist_html}</div></pre></div>"
        
        "<div class='decklist-content'>
          <button onclick='copyDecklist(this)' class='btn text-muted btn-sm decklist-copy-btn'>
            <i class='far fa-copy'></i>
          </button>
          <div class='card-preview'></div>
          <div class='copyable-decklist'><pre>#{newdecklist}</pre></div>
          <div class='display-decklist'>#{decklist_html}</div>
        </div>"
      end
  
      private
  
      def process_line(line)
        if line =~ /^(\d+)\s+(.*)$/
          quantity = $1
          card_name = $2.strip
          card_url = "https://scryfall.com/search?q=#{URI.encode_www_form_component(card_name)}"
          # card_image_url = "https://c1.scryfall.com/file/scryfall-cards/large/front/#{URI.encode_www_form_component(card_name).downcase.gsub(' ', '-')}.jpg"
          #card_html = "<a href='#{card_url}' class='card-link' data-cardname='#{card_name}' data-imageurl='#{card_image_url}' target='_blank'>#{card_name}</a>"
          card_html = "<a href='#{card_url}' class='card-link' data-cardname='#{URI.encode_www_form_component(card_name)}' target='_blank'>#{card_name}</a>"
          "#{quantity} #{card_html}<br>"
        else
          # Handle lines that don't match the quantity pattern
          card_name = line.strip
          if card_name.empty?
            ""
          else
            card_url = "https://scryfall.com/search?q=#{URI.encode_www_form_component(card_name)}"
            # card_image_url = "https://c1.scryfall.com/file/scryfall-cards/large/front/#{URI.encode_www_form_component(card_name).downcase.gsub(' ', '-')}.jpg"
            "<a href='#{card_url}' class='card-link' data-cardname='#{card_name}' target='_blank'>#{card_name}</a><br>"
          end
        end
      end
    end
  end
  
  Liquid::Template.register_tag('decklist', Jekyll::DecklistTag)
  