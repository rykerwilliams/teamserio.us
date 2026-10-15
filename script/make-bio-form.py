#!/usr/bin/env python3
"""Generate the Apps Script that builds the Team Serious bios form.

The questions live in _data/bio_questions.yml, not in the form, so the wording
is version-controlled and the form can be rebuilt from it. That matters
because the response spreadsheet's header row is the question TITLE: if the
wording in the form and the wording here drift apart, the answers can no
longer be mapped back to an id, and the bio pages cannot be generated.

    python3 script/make-bio-form.py        # writes script/make-bio-form.gs

Paste the result into https://script.google.com and run makeBioForm.
"""
import io, json, os, sys

try:
    import yaml
except ImportError:
    sys.exit("needs PyYAML:  pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPE = {"short": "addTextItem", "long": "addParagraphTextItem",
        "choice": "addMultipleChoiceItem", "scale": "addScaleItem",
        "upload": "addFileUploadItem", "email": "addTextItem"}


def main():
    spec = yaml.safe_load(io.open(os.path.join(ROOT, "_data/bio_questions.yml"),
                                  encoding="utf-8"))
    questions = [q for s in spec["sections"] for q in s["questions"]]

    titles = [q["q"] for q in questions]
    ids = [q["id"] for q in questions]
    dupe_t = sorted({t for t in titles if titles.count(t) > 1})
    dupe_i = sorted({i for i in ids if ids.count(i) > 1})
    if dupe_t:
        sys.exit(f"duplicate question titles, answers could not be mapped: {dupe_t}")
    if dupe_i:
        sys.exit(f"duplicate question ids: {dupe_i}")

    body = []
    for sec in spec["sections"]:
        page = f'  form.addPageBreakItem().setTitle({json.dumps(sec["title"])})'
        if sec.get("blurb"):
            page += f'.setHelpText({json.dumps(sec["blurb"].strip())})'
        body.append("\n" + page + ";")
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
                         f'[DriveApp.FileType.IMAGE]).setMaxFileSize(10);')
            if q.get("required"):
                v.append(f'  {q["id"]}.setRequired(true);')
            body.append("\n".join(v))

    out = ('''/**
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
    'For the bios on teamserio.us. Most of it is optional; answer what you ' +
    'feel like. One-word answers are a valid personality.');
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);
  form.setConfirmationMessage('Got it. Shout if you want anything changed.');
''' + "\n".join(body) + '''

  var ss = SpreadsheetApp.create('Team Serious \\u2014 Bios (responses)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('Edit the form : ' + form.getEditUrl());
  Logger.log('Send this one : ' + form.getPublishedUrl());
  Logger.log('Responses     : ' + ss.getUrl());
}
''')
    path = os.path.join(ROOT, "script/make-bio-form.gs")
    io.open(path, "w", encoding="utf-8").write(out)
    print(f"wrote {path}")
    print(f"  {len(questions)} questions across {len(spec['sections'])} sections")


if __name__ == "__main__":
    main()
