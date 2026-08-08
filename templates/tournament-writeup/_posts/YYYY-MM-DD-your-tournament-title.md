---
layout: default-with-decklists
title:  "YOUR TOURNAMENT NAME - YYYY.MM.DD"
subtitle: "A Report"
date:   YYYY-MM-DD 12:00:00 +0000
categories: tournament-writeup
tags: tsi tournament-writeup vintage
header_type: splash
header_img: ../assets/images/YYYY/MM/DD/banner.jpg
include_on_feed   : true
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

  BEFORE YOU START:
  1. Rename this file. Replace "YYYY-MM-DD" with the tournament's date
     (like 2026-08-08) and "your-tournament-title" with a short,
     lowercase, dash-separated version of the title (like
     "2026-08-08-summer-showdown.md").
  2. Fill in the block between the two "---" lines above (the "front
     matter"):
       - title / subtitle: shown at the top of the page
       - date: should match the date you used in the filename
       - header_img: the big banner photo — see IMAGES below
       - author: your name, and optionally a small square avatar photo.
         If you don't want one, delete the whole "avatar:" line.

  FIRST TIME WRITING FOR US?
  Add a small square photo of yourself to assets/images/avatars/ (see the
  placeholder file already in that folder for naming tips), then point
  "author: avatar:" at it above. Already written for us before? Reuse
  your existing avatar path if you know it, or just ask.

  IMAGES:
  Put every photo you use in this post inside:
      assets/images/YYYY/MM/DD/
  using the SAME date you used in the filename. Simple lowercase
  filenames, no spaces (01.jpg, trophy.jpg, etc).

  Single photo:
      ![Describe the photo](../assets/images/YYYY/MM/DD/01.jpg){: width="50%"}

  Side-by-side gallery of 3 related photos (must be .jpg files, put them
  in their own subfolder first, e.g. assets/images/YYYY/MM/DD/round-photos/):
      {% include image-gallery-no-caption-3-per-responsive.html folder="/assets/images/YYYY/MM/DD/round-photos" %}

  DECKLISTS:
  For each decklist, make a plain .txt file in
      assets/files/YYYY/MM/DD/Player Name - Deck Name.txt
  One card per line as "QUANTITY Card Name", e.g.:
      4 Ragavan, Nimble Pilferer
      1 Black Lotus
  Leave ONE blank line, then list sideboard cards the same way. See the
  example file already in that folder for a full sample.

  Then reference it in the post like this (see the Decklists section
  below for the exact pattern):
      {% deckfile /assets/files/YYYY/MM/DD/Player Name - Deck Name.txt %}

  Plain text editors only, please (Notepad, TextEdit, VS Code, etc.) —
  NOT Microsoft Word, which adds hidden formatting that breaks the file.
-->

[Opening paragraph: how many players, where it happened, and any context worth mentioning.]

## Philanthropy

<!-- Delete this whole section if it doesn't apply to your event. -->

[If you raised money for charity or did something similar, mention it here.]

## Vintage Play

### Metagame breakdown

<!--
  Group decks however makes sense for your event (by archetype, by
  colors, whatever). Each line is "Player – Deck Name".
-->

#### [Archetype Group 1]

1. Player Name – Deck Name
1. Player Name – Deck Name

#### [Archetype Group 2]

1. Player Name – Deck Name
1. Player Name – Deck Name

<!-- Optional: a side-by-side gallery of round photos -->
{% include image-gallery-no-caption-3-per-responsive.html folder="/assets/images/YYYY/MM/DD/round-photos" %}

### Top 8

1. Player Name – Deck Name
2. Player Name – Deck Name
3. Player Name – Deck Name
4. Player Name – Deck Name
5. Player Name – Deck Name
6. Player Name – Deck Name
7. Player Name – Deck Name
8. Player Name – Deck Name

[Decklists](#decklists) are below.

### Quarter Finals

[Results, e.g. "1. Player A Deck vs 8. Player B Deck – Player A wins 2-0"]

### Semi Finals

[Results]

### Finals

[Results]

### Decklists

<!--
  Repeat this block for each player whose decklist you're including.
  The photo is optional — delete the image line if you don't have one.
-->

##### *Player Name* - 1st

![Player Name](../assets/images/YYYY/MM/DD/top8/player-name.jpg){: width="35%"}
{% deckfile /assets/files/YYYY/MM/DD/Player Name - Deck Name.txt %}

##### *Player Name* - 2nd

![Player Name](../assets/images/YYYY/MM/DD/top8/player-name.jpg){: width="35%"}
{% deckfile /assets/files/YYYY/MM/DD/Player Name - Deck Name.txt %}

## We Are Friends, We Have Fun

[Closing thank-yous — hosts, helpers, anyone else worth mentioning.]

<!-- Optional: a gallery of general candid photos from the day -->
{% include image-gallery-no-caption-3-per-responsive.html folder="/assets/images/YYYY/MM/DD/candids" %}
