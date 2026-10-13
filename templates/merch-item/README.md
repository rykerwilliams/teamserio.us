# Merch Item Template

Got something you make that other people might want — shirts, playmats,
tokens, alters, stickers, prints? This puts it on the site's merch page.

**This is not a store.** There's no checkout and no payment. People
browse, add what they're interested in to a list, copy that list, and
message you directly. You work out price and payment between yourselves,
exactly like you would now. The site just saves everyone the back-and-forth
of "wait, which one did you mean?"

You don't need to know git, GitHub, or anything technical — just follow
these steps, then zip this whole folder back up and send it back.

## What's in here

```
README.md                                 <- this file
_merch/
  your-item-name.md                       <- the description of your item
assets/
  images/
    avatars/                              <- optional: your photo goes here
    merch/
      your-name/
        your-item/                        <- photos of your item go here
```

## Steps

1. **Open `_merch/your-item-name.md`** in a plain text editor (Notepad,
   TextEdit, VS Code — **not Microsoft Word**, which adds hidden
   formatting that breaks things).

2. **Rename the file itself** to something short, lowercase and
   dash-separated. Example: `logo-tee.md` or `swamp-alters.md`.

3. **Fill in the top section** (between the two `---` lines) — what it's
   called, your name, how to reach you, and a price. Line-by-line notes
   are inside the file itself as a comment block.

   **Don't put an email address in there.** These files are public on the
   internet and addresses get scraped for spam. Use your Discord or Slack
   handle instead — that's what the `creator_handle` line is for.

   First time? Add a small square photo of yourself to
   `assets/images/avatars/` (see the placeholder file there for naming
   tips) and point the `creator_avatar:` line at it. Don't want one?
   Delete the whole `creator_avatar:` line.

4. **About the price**: it's free text, so `$25`, `25`, `£20`, `trade`
   and `ask` all work. Anything that looks like a number gets added up
   when someone collects a few items; `trade` and `ask` are shown as
   written and left out of the total. If your price depends on size or
   options, put `ask` there and explain it in the description.

5. **Write the description** below that, replacing the placeholder text.
   What it is, what it's made of, what sizes or variants exist — anything
   someone would want to know before messaging you. Plain paragraphs are
   fine; bullet points work well for sizes and options.

6. **Add your photos**: put them in
   `assets/images/merch/your-name/your-item/`, renaming those last two
   folders to your name and your item (lowercase, dashes, no spaces —
   e.g. `rajah-james/logo-tee`). Name the main photo `main.jpg` and point
   the `header_img:` line at it. That's the one people see on the merch
   page, so make it the good one.

7. **Sold out, or not making them any more?** Set `available: false`.
   The item stays on the page but stops being addable. No need to send
   anything back — just ask and we'll flip it.

8. **When you're done**, select this whole folder (the one with this
   README in it) and compress it into a .zip file, then send it back.
   Don't worry about anything else — formatting it for the website is
   handled on this end.

Questions? Just ask — no need to get it perfect.
