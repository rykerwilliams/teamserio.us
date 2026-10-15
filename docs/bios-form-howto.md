# Making the bios form live

The form is built by a script rather than by hand, so that the questions stay
in the repo (`_data/bio_questions.yml`) and the form can be rebuilt from them.
Running it takes about two minutes.

## Once

1. Go to **https://script.google.com** and click **New project**.
2. Delete the stub `function myFunction() {}` in the editor.
3. Paste the whole of `script/make-bio-form.gs`.
4. Give the project a name — "Team Serious bios" — so you can find it later.
5. **Run ▸ makeBioForm.**
6. Google will ask for permission twice: once to manage forms and files, once
   to send mail as you. The second is the nudge; without it the form still
   works, people just never get their link back.
7. Open **Execution log**. It prints three links:

   ```
   Edit the form : https://docs.google.com/forms/d/.../edit
   Send this one : https://docs.google.com/forms/d/e/.../viewform
   Responses     : https://docs.google.com/spreadsheets/d/...
   ```

   Keep all three. The middle one is what you send the team.

## It is already live

A form accepts responses the moment it exists — there is no publish button.
To stop it later, open the form, **Responses** tab, and turn off *Accepting
responses*.

## What happens when someone answers

- The answers land in the responses spreadsheet, one row per person, one
  column per question.
- If they gave an email address, the script sends them **one** message with a
  link back into their own answers, so they can finish the rest later or
  change something. Only once, even if they edit afterwards.
- If they stopped at the fork partway through, their partial answers are
  still submitted and still useful.

## Changing a question

Edit `_data/bio_questions.yml`, run `python3 script/make-bio-form.py`, and
paste the regenerated script into a **new** Apps Script run to build a fresh
form. Do not edit question wording in the Google Forms UI: the response
sheet's header row is the question title, so editing it there breaks the link
between an answer and the `id` it belongs to, and the bio pages cannot be
generated.

Small wording fixes to help text are safe. Question titles are not.

## Known limits

- Mail is sent from your own Gmail, with the usual consumer quota of about
  100 a day. Not a concern for a team this size.
- The one-nudge-per-address record lives in that Apps Script project's
  properties. Build a second form from scratch and everyone becomes eligible
  for one more nudge.
