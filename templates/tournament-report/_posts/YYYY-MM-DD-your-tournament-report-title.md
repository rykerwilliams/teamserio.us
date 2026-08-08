---
layout: default-with-decklists
title:  "YOUR TOURNAMENT REPORT TITLE HERE"
date:    YYYY-MM-DD 12:00:00 +0000
categories: tournament-report
tags: vintage tournament-report
include_on_feed: true
show_author       : true
show_bottomnavs   : true
show_categories   : true
show_comments     : true
show_date         : true
show_related      : true
show_sociallinks  : true
show_tags         : true
author:
  name: YOUR NAME HERE
  avatar: ../assets/images/avatars/YOUR-AVATAR-HERE.jpg
  location: City, State/Country
---

<!--
  READ ME FIRST
  This whole comment block (everything between "<!--" and "-->") is
  invisible once the post is published — it's just notes for you while
  you're writing. Delete these comments as you go, or leave them, it
  won't matter.

  This is a personal tournament report — your own story of playing in
  the event (deck choice, prep, round-by-round matches, how you did).
  That's different from a "tournament-writeup," which is an organizer's
  overview of the whole event for everyone (metagame breakdown, top 8,
  other players' decklists). If you're writing about the event as a
  whole rather than your own run, ask about the other template instead.

  Everything above this comment (title, date, tags, author, etc.) is
  already set up with the site's normal defaults — you only need to
  touch:
    - title
    - date (should match the date you use in the filename below)
    - tags (add anything specific to this event, e.g. the event name)
    - author: name / avatar / location

  BEFORE YOU START:
  1. Rename this file. Replace "YYYY-MM-DD" with the date the write-up
     is posted (like 2026-08-08) and "your-tournament-report-title" with
     a short, lowercase, dash-separated version of your title (like
     "2026-08-08-my-summer-showdown-run.md").
  2. Fill in title, date, and author above.

  FIRST TIME WRITING FOR US?
  Add a small square photo of yourself to assets/images/avatars/ (see
  the placeholder file already in that folder for naming tips), then
  point "author: avatar:" at it above. Already written for us before?
  Reuse your existing avatar path if you know it, or just ask.

  IMAGES:
  Put every photo you use in this post inside assets/images/YYYY/MM/DD/
  (same date as your filename), simple lowercase names, no spaces, then:
      ![Describe the photo](../assets/images/YYYY/MM/DD/01.jpg){: width="50%"}

  DECKLIST:
  Make a plain .txt file at
      assets/files/YYYY/MM/DD/Your Name - Your Deck.txt
  One card per line as "QUANTITY Card Name", a blank line, then any
  sideboard cards the same way. There's a real example already in that
  folder — open it to see the exact format. Reference it like this
  (this is what "layout: default-with-decklists" up top is for — don't
  change that line):
      {% deckfile /assets/files/YYYY/MM/DD/Your Name - Your Deck.txt %}

  STRUCTURE:
  Below is a skeleton that mirrors how these reports usually go: intro,
  prep, then a section per day, with a subsection per round, and a
  sub-subsection per game within a round. Copy/paste the "Round" and
  "Game" blocks as many times as you need (however many rounds you
  played), and delete whatever sections don't apply to you (not everyone
  travels, not everyone makes Day 2, etc). This is a personal story, not
  a form — reorganize however fits how your event actually went.

  Plain text editors only, please (Notepad, TextEdit, VS Code, etc.) —
  NOT Microsoft Word, which adds hidden formatting that breaks the file.
-->

*[Optional: note where else this was posted, if anywhere.]*

## Intro

[A few sentences setting up the report: what event, when, why you're writing this, and a heads up if it's long.]

## Preparation

[How you picked your deck, testing, trades/purchases, anything interesting that happened before the event even started.]

![Describe the photo](../assets/images/YYYY/MM/DD/01.jpg){: width="50%"}

## Day 0 - Travel

[Optional section: getting there, meeting up with friends, settling in.]

## Day 1 - Swiss

<!--
  Copy this "Round" block once per round you played. Each round can
  have as many "Game" sub-blocks as games you actually played.
-->

### Round 1 [Opponent Name] [Their Deck]

[How the round went overall — result, key plays, notable moments.]

#### R1 G1 - [who's on the play, opening hands, etc.]

[Blow-by-blow, as detailed or brief as you like.]

#### R1 G2 - [...]

[...]

<!-- Repeat the "### Round N ..." block above for Rounds 2, 3, 4, etc. -->

### Celebration

[Optional: how the day ended, standings, how you felt going into Day 2/3.]

## Day 2 - [Between Rounds / Rest Day]

[Optional section, if your event had one: testing, meals, hanging out.]

## Day 3 - Top 8

<!-- Same pattern as Swiss rounds, renamed for elimination rounds. -->

### Quarterfinal - [Opponent Name]

#### Quarterfinal - G1 - [...]

[...]

### Semifinal - [Opponent Name]

[...]

### Final - [Opponent Name]

[...]

## Decklist

![Your Name](../assets/images/YYYY/MM/DD/top8/your-name.jpg){: width="35%"}
{% deckfile /assets/files/YYYY/MM/DD/Your Name - Your Deck.txt %}

## Closing Thoughts

[How you feel looking back, what you'd change, what's next.]

## Thanks

[Shoutouts — people who helped with testing, travel, hosting, whatever's worth mentioning.]
