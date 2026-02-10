require 'net/http'
require 'uri'

module Jekyll
  class CalendarFetcher < Generator
    safe true
    priority :low

    def generate(site)
      calendar_url = 'https://calendar.google.com/calendar/ical/7e9b3211f2ce55f311f896ae5888b0b23f9c65ac327fa1b493f6562b163e9ca2%40group.calendar.google.com/public/basic.ics'

      begin
        puts "Fetching calendar data from Google Calendar..."
        uri = URI.parse(calendar_url)
        response = Net::HTTP.get_response(uri)

        if response.is_a?(Net::HTTPSuccess)
          site.data['calendar_ics'] = response.body
          puts "Calendar data fetched successfully (#{response.body.length} bytes)"
        else
          puts "Failed to fetch calendar: #{response.code} #{response.message}"
          site.data['calendar_ics'] = nil
        end
      rescue => e
        puts "Error fetching calendar: #{e.message}"
        site.data['calendar_ics'] = nil
      end
    end
  end
end
