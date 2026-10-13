# _plugins/external_links.rb
#
# Every link that leaves the site opens in a new tab and carries
#     target="_blank" rel="noopener noreferrer"
#
# Why a :post_render hook and not a Generator, like mtg_autocard.rb: almost
# every link here is written in Markdown, so at generator time doc.content is
# still Markdown and contains no <a> tags at all. The anchors only exist once
# the converter has run, and the layout's own links (nav, footer) only exist
# after that. :post_render sees the finished page.
#
# This also normalises what was already there by hand. Across the posts there
# were four spellings, and 41 anchors carried "noreferer" -- a single 'r', not
# a real rel token, so those links were still sending a referrer. Existing
# nofollow/ugc tokens are preserved; only the misspelling is corrected and the
# two required tokens added.
#
# Sources are left untouched. This rewrites output only.

require "uri"
require "set"

module ExternalLinks
  # Never rewrite inside these. An <a> tag is unlikely in a <script>, but
  # mtg_autocard.rb learned the hard way what regex rewriting does to inline
  # JavaScript, so this plugin follows the same discipline.
  SKIP = %r{(<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|
             <pre\b[^>]*>.*?</pre>|<code\b[^>]*>.*?</code>)}mix

  ANCHOR = /<a\b([^>]*?)>/im
  HREF   = /\bhref\s*=\s*(["'])(.*?)\1/im
  REL    = /\brel\s*=\s*(["'])(.*?)\1/im
  TARGET = /\btarget\s*=\s*(["'])(.*?)\1/im

  REQUIRED = %w[noopener noreferrer].freeze

  def self.local_hosts(site)
    hosts = Set.new
    [site.config["url"]].compact.each do |u|
      h = begin URI.parse(u.to_s).host rescue nil end
      hosts << h.downcase if h
    end
    hosts
  end

  # Characters that are invisible in an editor but make URI.parse raise. Several
  # hrefs in the posts end in U+2060 WORD JOINER, pasted in from elsewhere, and
  # one carries a trailing space. An early version of this plugin rescued the
  # exception and returned "not external", so those links were skipped silently
  # and kept their misspelled rel. Failing open on a malformed URL is the wrong
  # default for a security attribute, so strip the junk and parse what remains.
  INVISIBLE = /[\u200B-\u200F\u2028\u2029\u2060-\u2064\uFEFF]/.freeze

  def self.host_of(href)
    cleaned = href.strip.gsub(INVISIBLE, "")
    begin
      h = URI.parse(cleaned).host
      return h unless h.nil? || h.empty?
    rescue StandardError
      # fall through to the textual match below
    end
    # URI.parse still rejects plenty of real-world hrefs -- unescaped spaces in
    # a path, for one. The host is unambiguous without a full parse.
    m = cleaned.match(%r{\A(?:https?:)?//([^/?#]+)}i)
    m && m[1].split("@").last.split(":").first
  end

  def self.external?(href, hosts)
    return false if href.nil? || href.empty?
    return false if href.start_with?("#", "?")
    # A single leading slash is site-relative; "//" is protocol-relative and may
    # well point somewhere else entirely.
    return false if href.start_with?("/") && !href.start_with?("//")
    # mailto:, tel:, javascript: and friends are not navigations we retarget.
    return false unless href.strip =~ %r{\A(https?:)?//}i
    host = host_of(href)
    return false if host.nil? || host.empty?
    !hosts.include?(host.downcase)
  end

  def self.fix_rel(existing)
    tokens = existing.to_s.split(/\s+/).reject(&:empty?)
    # "noreferer" (one r) is not a rel token; it was a typo repeated across the
    # posts. Correct it rather than leaving a dead attribute beside the real one.
    tokens = tokens.map { |t| t.casecmp("noreferer").zero? ? "noreferrer" : t }
    (tokens + REQUIRED).uniq { |t| t.downcase }.join(" ")
  end

  def self.rewrite(html, hosts)
    html.gsub(ANCHOR) do
      tag, attrs = Regexp.last_match(0), Regexp.last_match(1)
      href = attrs[HREF, 2]
      next tag unless external?(href, hosts)

      out = attrs
      out = if out =~ REL
              out.sub(REL) { %Q{rel="#{fix_rel(Regexp.last_match(2))}"} }
            else
              out + %Q{ rel="#{REQUIRED.join(" ")}"}
            end
      # Respect an explicit target someone set on purpose.
      out += %Q{ target="_blank"} unless out =~ TARGET
      "<a#{out}>"
    end
  end

  def self.process(html, hosts)
    return html if html.nil?
    html.split(SKIP).map do |part|
      part =~ /\A<(script|style|pre|code)\b/im ? part : rewrite(part, hosts)
    end.join
  end
end

Jekyll::Hooks.register [:pages, :documents], :post_render do |doc|
  next unless doc.output
  ext = doc.respond_to?(:output_ext) ? doc.output_ext : File.extname(doc.path)
  next unless ext == ".html"
  doc.output = ExternalLinks.process(doc.output, ExternalLinks.local_hosts(doc.site))
end
