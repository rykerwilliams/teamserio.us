require 'uri'

module Jekyll
    class DecklistTag < Liquid::Block
      def initialize(tag_name, text, tokens)
        super
      end
  
      def render(context)
        # Initialize variables for sideboard detection
        decklist_html = ""
        
        decklist = super
        decklist.split("\n").each do |line|
          # Check for "Sideboard" and toggle the sideboard flag
          # Process mainboard cards
          decklist_html += process_line(line)
        end
  
        "<div class='decklist-content'>#{decklist_html}</div>"
      end
  
      private
  
      def process_line(line)
        if line =~ /^(\d+)\s+(.*)$/
          quantity = $1
          card_name = $2.strip
          card_url = "https://scryfall.com/search?q=#{URI.encode_www_form_component(card_name)}"
          # card_image_url = "https://c1.scryfall.com/file/scryfall-cards/large/front/#{URI.encode_www_form_component(card_name).downcase.gsub(' ', '-')}.jpg"
          #card_html = "<a href='#{card_url}' class='card-link' data-cardname='#{card_name}' data-imageurl='#{card_image_url}' target='_blank'>#{card_name}</a>"
          card_html = "<a href='#{card_url}' class='card-link' data-cardname='#{card_name}' target='_blank'>#{card_name}</a>"
          "#{quantity} #{card_html}<br>"
        else
          # Handle lines that don't match the quantity pattern
          card_name = line.strip
          if card_name.empty?
            "<br>"
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
  