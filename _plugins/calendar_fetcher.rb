require 'net/http'
require 'uri'
require 'fileutils'

# Embeds the public Google Calendar feed into the build so the calendar page
# can render without a client-side cross-origin fetch.
#
# Previously this rescued every failure to nil, which meant a transient network
# blip produced a *successful* build whose calendar page told visitors
# "Calendar data not available. Please rebuild the site." Failure was silent in
# CI and loud on the live site, which is exactly backwards.
#
# Now: fetch, fall back to the committed snapshot, and fail the build only when
# there is neither. A stale calendar is better than a red error box; no
# calendar at all should stop the deploy.
module Jekyll
  class CalendarFetcher < Generator
    safe true
    priority :low

    CALENDAR_URL = 'https://calendar.google.com/calendar/ical/' \
      '7e9b3211f2ce55f311f896ae5888b0b23f9c65ac327fa1b493f6562b163e9ca2' \
      '%40group.calendar.google.com/public/basic.ics'.freeze

    CACHE_PATH   = File.join('_data', 'calendar.ics').freeze
    OPEN_TIMEOUT = 10
    READ_TIMEOUT = 20
    MIN_BYTES    = 50   # anything smaller is not a usable VCALENDAR

    def generate(site)
      cache = File.join(site.source, CACHE_PATH)
      ics   = fetch unless ENV['CALENDAR_OFFLINE']

      if ics
        site.data['calendar_ics'] = ics
        write_cache(cache, ics)
        return
      end

      if File.exist?(cache)
        stale = File.read(cache)
        age   = ((Time.now - File.mtime(cache)) / 86_400).round
        warn_ci "Calendar fetch failed; using the committed snapshot from " \
                "#{CACHE_PATH} (#{age} day(s) old). Events added since then are missing."
        site.data['calendar_ics'] = stale
        return
      end

      raise Jekyll::Errors::FatalException,
            "Calendar fetch failed and no snapshot exists at #{CACHE_PATH}. " \
            "Refusing to publish a calendar page that tells visitors to rebuild the site. " \
            "Commit a snapshot, or set CALENDAR_OFFLINE=1 to build without one."
    end

    private

    def fetch
      uri = URI.parse(CALENDAR_URL)
      Jekyll.logger.info 'Calendar:', 'fetching from Google Calendar...'
      res = Net::HTTP.start(uri.host, uri.port, use_ssl: true,
                            open_timeout: OPEN_TIMEOUT, read_timeout: READ_TIMEOUT) do |http|
        http.request(Net::HTTP::Get.new(uri))
      end

      unless res.is_a?(Net::HTTPSuccess)
        warn_ci "Calendar fetch returned #{res.code} #{res.message}."
        return nil
      end

      body = res.body.to_s
      # A truncated or error body would otherwise be cached over a good snapshot.
      if body.bytesize < MIN_BYTES || !body.include?('BEGIN:VCALENDAR')
        warn_ci "Calendar response was not a valid VCALENDAR (#{body.bytesize} bytes)."
        return nil
      end

      Jekyll.logger.info 'Calendar:', "fetched #{body.bytesize} bytes"
      body
    rescue StandardError => e
      warn_ci "Calendar fetch failed: #{e.class}: #{e.message}"
      nil
    end

    def write_cache(path, body)
      return if File.exist?(path) && File.read(path) == body
      FileUtils.mkdir_p(File.dirname(path))
      File.write(path, body)
      Jekyll.logger.info 'Calendar:', "snapshot updated at #{CACHE_PATH}"
    rescue StandardError => e
      Jekyll.logger.warn 'Calendar:', "could not update snapshot: #{e.message}"
    end

    # Surfaces in the GitHub Actions run summary, not just the build log.
    def warn_ci(msg)
      puts "::warning::#{msg}" if ENV['GITHUB_ACTIONS']
      Jekyll.logger.warn 'Calendar:', msg
    end
  end
end
