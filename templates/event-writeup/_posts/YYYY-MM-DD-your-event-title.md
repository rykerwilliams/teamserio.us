---
layout: default
title: "YOUR EVENT TITLE HERE"
subtitle: "A Report"
categories: event-writeup
tags: tsi event-writeup
header_type: splash
header_img: ../assets/images/YYYY/MM/DD/header.jpg
date: YYYY-MM-DD 12:00:00 +0000
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
  you're writing. Feel free to delete these comments as you go, or leave
  them, it won't matter.

  BEFORE YOU START:
  1. Rename this file. Replace "YYYY-MM-DD" with the actual date of the
     event (like 2026-08-08) and "your-event-title" with a short,
     lowercase, dash-separated version of your title (like
     "2026-08-08-summer-showdown.md").
  2. Fill in the block between the two "---" lines above (that's called
     "front matter"):
       - title / subtitle: shown at the top of the page
       - date: should match the date you used in the filename
       - header_img: the big banner photo — see IMAGES below
       - author: your name, and optionally a small square photo of
         yourself (see IMAGES below). If you don't want an avatar photo,
         just delete the whole "avatar:" line.
  3. Write your report below using the placeholders as a guide, then
     delete the placeholders.

  IMAGES:
  Put every photo you use in this post inside:
      assets/images/YYYY/MM/DD/
  (using the SAME date you used in the filename). Give each photo a
  simple lowercase name with no spaces, like 01.jpg, 02.jpg, trophy.jpg.

  To show a single photo in the text, write:
      ![Describe what's in the photo](../assets/images/YYYY/MM/DD/01.jpg){: width="50%"}
  The width is roughly how much of the page it takes up — 40-80% usually
  looks good for one photo on its own.

  FIRST TIME WRITING FOR US?
  Add a small square photo of yourself to assets/images/avatars/ (see the
  placeholder file already in that folder for naming tips), then point
  "author: avatar:" at it above. Already written for us before? Reuse
  your existing avatar path if you know it, or just ask.

  Plain text editors only, please (Notepad, TextEdit, VS Code, etc.) —
  NOT Microsoft Word, which adds hidden formatting that breaks the file.
-->

[Write 2-3 sentences introducing the event: what it was, where it happened, and why people should care.]

## [Section Title — e.g. "How It Went"]

[Tell the story here. Regular paragraphs, no special formatting required.]

![Describe what's in the photo](../assets/images/YYYY/MM/DD/01.jpg){: width="50%"}

## [Another Section]

[More of the story...]

<!--
  OPTIONAL — SIDE-BY-SIDE PHOTO GALLERY
  If you have 3 photos that belong together (like a trio of shots from
  the same moment), you can show them side-by-side instead of one after
  another. To do that:
    1. Put those 3 photos in their OWN subfolder, e.g.
       assets/images/YYYY/MM/DD/some-moment/01.jpg, 02.jpg, 03.jpg
       (they must be .jpg files for this to work).
    2. Use this line where you want the gallery to appear:
       {% include image-gallery-no-caption-3-per-responsive.html folder="/assets/images/YYYY/MM/DD/some-moment" %}

  If this doesn't make sense, don't worry about it — just use single
  photos like the example above, as many times as you need.
-->

{% include image-gallery-no-caption-3-per-responsive.html folder="/assets/images/YYYY/MM/DD/some-moment" %}

## Wrap-Up

[A closing paragraph — thank yous, what's next, etc.]
