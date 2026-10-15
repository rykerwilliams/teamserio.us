#!/usr/bin/env python3
"""Generate the Apps Script that builds the Team Serious bios form.

The questions live in _data/bio_questions.yml, not in the form, so the wording
is version-controlled and the form can be rebuilt from it. That matters
because the response spreadsheet's header row is the question TITLE: if the
wording in the form and the wording here drift apart, the answers can no
longer be mapped back to an id, and the bio pages cannot be generated.

Two things the form has to get right, because it is long:

  * SAVE AND COME BACK. Forms autosaves a draft for anyone signed in to a
    Google account, for 30 days, and that is what the form leans on. It does
    NOT collect email addresses: Google would then mail each respondent a
    receipt containing a link back into their answers, which is a stronger
    guarantee, but it is not worth making everyone hand over an address.
    There is an optional email QUESTION at the end for anyone happy to give
    one, and that lands in the sheet like any other answer.

  * A WAY OUT EARLY. Forms cannot be submitted part-way through: someone who
    gives up on page four leaves nothing at all behind. So the sections
    marked `core:` come first and end with a fork -- keep going, or stop and
    submit what you have. Answering only the core set takes a few minutes and
    still produces a usable bio.

    python3 script/make-bio-form.py
"""
import io, json, os, re, sys

try:
    import yaml
except ImportError:
    sys.exit("needs PyYAML:  pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPE = {"short": "addTextItem", "long": "addParagraphTextItem",
        "choice": "addMultipleChoiceItem", "scale": "addScaleItem",
        "upload": "addFileUploadItem", "email": "addTextItem"}

HEAD = '''/**
 * Builds the Team Serious bios form.
 *
 * Paste this whole file into a new project at https://script.google.com,
 * then Run > makeBioForm. The execution log prints the form's edit URL, the
 * URL to send people, and the response spreadsheet.
 *
 * GENERATED from _data/bio_questions.yml by script/make-bio-form.py. Edit the
 * YAML and regenerate rather than editing this file: the response sheet's
 * header row is the question title, so if the two drift the answers can no
 * longer be mapped back to an id.
 */
function makeBioForm() {
  var form = FormApp.create('Team Serious \\u2014 Bios');
  form.setDescription(
    'For the bios on teamserio.us. Only four questions are required \\u2014 ' +
    'answer whatever else you feel like. One-word answers are a valid ' +
    'personality.\\n\\n' +
    'If you are signed in to a Google account it saves your progress as you ' +
    'go, so you can close the tab and pick it up later. You can also stop ' +
    'after the first few pages and submit what you have \\u2014 there is a ' +
    'point partway through that offers exactly that.');

  // No email collection: nobody is made to hand over an address to answer a
  // questionnaire about mustard. Forms autosaves a draft for signed-in
  // respondents for 30 days, which covers coming back, and the fork partway
  // through means a half-finished form can still be submitted rather than
  // lost. There is an optional email question at the end for anyone willing.
  form.setCollectEmail(false);
  form.setAllowResponseEdits(true);
  form.setProgressBar(true);
  form.setConfirmationMessage(
    'Got it \\u2014 thank you.\\n\\n' +
    'Keep the link on this page if you want to edit your answers later, or ' +
    'just tell us and we will fix it. If you stopped early you can reopen ' +
    'the form any time to do the rest.');
'''

TAIL = '''
  var ss = SpreadsheetApp.create('Team Serious \\u2014 Bios (responses)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('Edit the form : ' + form.getEditUrl());
  Logger.log('Send this one : ' + form.getPublishedUrl());
  Logger.log('Responses     : ' + ss.getUrl());
}
'''


def var_for(title):
    return "page_" + re.sub(r"[^a-z0-9]+", "_", title.lower()).strip("_")


def main():
    spec = yaml.safe_load(io.open(os.path.join(ROOT, "_data/bio_questions.yml"),
                                  encoding="utf-8"))
    sections = spec["sections"]
    questions = [q for s in sections for q in s["questions"]]

    titles = [q["q"] for q in questions]
    ids = [q["id"] for q in questions]
    dupe_t = sorted({t for t in titles if titles.count(t) > 1})
    dupe_i = sorted({i for i in ids if ids.count(i) > 1})
    if dupe_t:
        sys.exit(f"duplicate question titles, answers could not be mapped: {dupe_t}")
    if dupe_i:
        sys.exit(f"duplicate question ids: {dupe_i}")

    core = [s for s in sections if s.get("core")]
    last_core = core[-1] if core else None
    first_optional = next((s for s in sections if s.get("optional")), None)

    out = [HEAD]
    for sec in sections:
        page = f'  var {var_for(sec["title"])} = form.addPageBreakItem()' \
               f'.setTitle({json.dumps(sec["title"])})'
        if sec.get("blurb"):
            page += f'.setHelpText({json.dumps(sec["blurb"].strip())})'
        out.append("\n" + page + ";")

        for q in sec["questions"]:
            call = ("addCheckboxItem" if q["type"] == "choice" and q.get("multi")
                    else TYPE[q["type"]])
            v = [f'  var {q["id"]} = form.{call}();',
                 f'  {q["id"]}.setTitle({json.dumps(q["q"])});']
            if q.get("help"):
                v.append(f'  {q["id"]}.setHelpText({json.dumps(q["help"].strip())});')
            if q.get("options"):
                v.append(f'  {q["id"]}.setChoiceValues({json.dumps(q["options"])});')
            if q["type"] == "upload":
                v.append(f'  {q["id"]}.setAllowedFileTypes('
                         '[DriveApp.FileType.IMAGE]).setMaxFileSize(10);')
            if q.get("required"):
                v.append(f'  {q["id"]}.setRequired(true);')
            out.append("\n".join(v))

        if sec is last_core and first_optional:
            out.append(
                '  var keep_going = form.addMultipleChoiceItem();\n'
                '  keep_going.setTitle('
                '"That is everything we actually need. Keep going?");\n'
                '  keep_going.setHelpText(\n'
                '    "The rest is the fun half: the questionnaire, and '
                'the one about gas " +\n'
                '    "station food. Stopping here still gives us a page, '
                'and you " +\n'
                '    "can open the form again later to finish the rest.");\n'
                '  keep_going.setRequired(true);')

    if last_core and first_optional:
        out.append(f'''
  // Wired once every page exists: a choice cannot point at a page that has
  // not been created yet. "Stop here" skips to the final page so the form can
  // actually be submitted -- Forms has no part-way submit, and without this a
  // long form means people who give up leave nothing behind at all.
  keep_going.setChoices([
    keep_going.createChoice("Keep going", {var_for(first_optional["title"])}),
    keep_going.createChoice("Stop here \\u2014 I will finish it later",
                            {var_for(sections[-1]["title"])})
  ]);''')

    out.append(TAIL)
    path = os.path.join(ROOT, "script/make-bio-form.gs")
    io.open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote {path}")
    print(f"  {len(questions)} questions across {len(sections)} sections")
    print(f"  core: {sum(len(s['questions']) for s in core)} questions, "
          f"then a fork")
    print(f"  required: {sum(1 for q in questions if q.get('required'))}")


if __name__ == "__main__":
    main()
