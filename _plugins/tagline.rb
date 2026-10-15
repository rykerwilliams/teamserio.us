# Picks the home page tagline from _data/taglines.yml.
#
# chulapa builds the home page title as:
#
#     site.subtitle | default: site.github.project_tagline
#
# and `subtitle` was unset, so it fell through to the GitHub repository's
# description -- which read "testing". That is invisible from a checkout,
# which is why it survived so long. Setting it here keeps the value in the
# repository, where it is reviewable, and lets the list grow without touching
# any configuration.
#
# The choice is DETERMINISTIC: the same commit always yields the same tagline,
# so rebuilding a commit does not quietly change what a shared link says. It
# is seeded from the commit SHA when one is available (GitHub Actions sets
# GITHUB_SHA) and from the build date otherwise.
# :post_read, not :after_init -- site.data is not populated until the site has
# been read, so an :after_init hook sees no taglines at all and silently does
# nothing.
Jekyll::Hooks.register :site, :post_read do |site|
  taglines = site.data && site.data["taglines"]
  next if taglines.nil? || taglines.empty?

  seed = ENV["GITHUB_SHA"] || Time.now.strftime("%Y-%m-%d")
  index = seed.each_char.sum(&:ord) % taglines.length
  site.config["subtitle"] = taglines[index]
end
