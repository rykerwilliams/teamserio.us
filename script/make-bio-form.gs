/**
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
  var form = FormApp.create('Team Serious \u2014 Bios');
  form.setDescription(
    'For the bios on teamserio.us. Most of it is optional; answer what you ' +
    'feel like. One-word answers are a valid personality.');
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setAllowResponseEdits(true);
  form.setConfirmationMessage('Got it. Shout if you want anything changed.');

  form.addPageBreakItem().setTitle("Who you are").setHelpText("The part that ends up at the top of your page. Keep it short; the interesting stuff is further down.");
  var name = form.addTextItem();
  name.setTitle("Name, as you want it on the site");
  name.setRequired(true);
  var handle = form.addTextItem();
  handle.setTitle("Handle(s) \u2014 TMD, Discord, wherever you post");
  handle.setHelpText("So we can credit old posts and decklists to the right person.");
  var where = form.addTextItem();
  where.setTitle("Where are you?");
  where.setHelpText("City and state is plenty. 'Leng' is also an accepted answer.");
  var photo = form.addFileUploadItem();
  photo.setTitle("A photo of you");
  photo.setHelpText("Playing, holding a trophy, or just a face. We can also pull one from an event report if you'd rather.");
  photo.setAllowedFileTypes([DriveApp.FileType.IMAGE]).setMaxFileSize(10);
  var links = form.addParagraphTextItem();
  links.setTitle("Anywhere you want linked");
  links.setHelpText("Podcast, YouTube, Bluesky, store, band. One per line.");

  form.addPageBreakItem().setTitle("How you got here");
  var started = form.addTextItem();
  started.setTitle("When did you start playing, and what pulled you in?");
  var first_deck = form.addParagraphTextItem();
  first_deck.setTitle("First deck you were proud of");
  var found_ts = form.addParagraphTextItem();
  found_ts.setTitle("How did you end up with Team Serious?");
  found_ts.setHelpText("Who dragged you in, and to which event.");
  found_ts.setRequired(true);
  var formats = form.addCheckboxItem();
  formats.setTitle("What do you actually play these days?");
  formats.setChoiceValues(["Vintage", "Old School 93/94", "Middle School", "Premodern", "Legacy", "Commander", "Ohio Ante", "Limited", "Whatever is on the table"]);
  var pet_deck = form.addParagraphTextItem();
  pet_deck.setTitle("Your deck. The one people associate with you.");
  pet_deck.setHelpText("What it is, why you keep sleeving it, and what it never beats.");

  form.addPageBreakItem().setTitle("The record").setHelpText("Anything you want on the page as a credit. Modesty is not useful here.");
  var finishes = form.addParagraphTextItem();
  finishes.setTitle("Notable finishes?");
  var proudest = form.addParagraphTextItem();
  proudest.setTitle("The win you're proudest of, which may not be the biggest one");
  var beat = form.addParagraphTextItem();
  beat.setTitle("The loss you still think about");

  form.addPageBreakItem().setTitle("The Team Serious questionnaire").setHelpText("The actual point of the exercise. Answer at whatever length you like; one-word answers are a valid personality.");
  var fav_member = form.addTextItem();
  fav_member.setTitle("Favorite Team Serious member");
  fav_member.setHelpText("Wrong answers will be published.");
  var licorice = form.addMultipleChoiceItem();
  licorice.setTitle("Straight up: black licorice?");
  licorice.setChoiceValues(["Yes", "No", "Only under duress", "I need to tell you a story about this"]);
  var appetizing = form.addTextItem();
  appetizing.setTitle("What Magic card looks most appetizing to you?");
  var garfield = form.addParagraphTextItem();
  garfield.setTitle("You can ask Richard Garfield one question. What is it?");
  var collection_age = form.addTextItem();
  collection_age.setTitle("What percentage of your collection is old enough to drive? Drink? Rent a car?");
  var color = form.addMultipleChoiceItem();
  color.setTitle("Favorite Magic color, because it's corny AF");
  color.setChoiceValues(["White", "Blue", "Black", "Red", "Green", "Colorless, and I'd like to explain"]);
  var fruit = form.addTextItem();
  fruit.setTitle("Favorite fruit-themed card?");
  var pentagram = form.addTextItem();
  pentagram.setTitle("Which Magic card would look better with a pentagram on it?");
  var upkeep = form.addTextItem();
  upkeep.setTitle("What would your cumulative upkeep be, if you had one?");
  var family = form.addParagraphTextItem();
  family.setTitle("Who else in your family plays? What do your parents make of it?");
  var sandwich = form.addMultipleChoiceItem();
  sandwich.setTitle("Sandwich punch? In?");
  sandwich.setChoiceValues(["In", "Out", "Explain the rules again"]);
  var hotdogs = form.addTextItem();
  hotdogs.setTitle("How many hot dogs could you eat in under 10 minutes?");
  var forty = form.addMultipleChoiceItem();
  forty.setTitle("Hour Power or Edward 40 Hands?");
  forty.setChoiceValues(["Hour Power", "Edward 40 Hands", "Neither, I have children now"]);
  var mustard = form.addMultipleChoiceItem();
  mustard.setTitle("Stadium mustard or ballpark mustard?");
  mustard.setChoiceValues(["Stadium", "Ballpark", "This question is beneath me"]);
  var proxy = form.addMultipleChoiceItem();
  proxy.setTitle("Proxies: where do you land?");
  proxy.setChoiceValues(["Real cards or nothing", "Proxy the power, own the rest", "Full proxy, more games", "Depends who's asking"]);
  var worst_take = form.addParagraphTextItem();
  worst_take.setTitle("Your worst Magic take, stated with full confidence");

  form.addPageBreakItem().setTitle("The 20th anniversary interviews").setHelpText("For the anniversary we want to record a run of short \"life story\" interviews \u2014 about fifteen minutes each, two or three per episode, so nothing runs past half an hour. No prep and no wrong answers: how you found Magic, how you found us, one object you bring along, one story you always tell, and some rapid-fire nonsense. You finish by asking a question of whoever is up next, without knowing who that is.");
  var interview = form.addMultipleChoiceItem();
  interview.setTitle("Want to do a 15-minute life story interview for the 20th?");
  interview.setChoiceValues(["Yes", "Yes, but talk me through it first", "Maybe later in the year", "No thanks"]);
  interview.setRequired(true);
  var interview_when = form.addCheckboxItem();
  interview_when.setTitle("If yes, when are you usually free?");
  interview_when.setHelpText("Rough is fine. We will work around you.");
  interview_when.setChoiceValues(["Weekday evenings", "Weekend afternoons", "Weekend evenings", "During an event", "Ask me, it varies"]);
  var interview_how = form.addMultipleChoiceItem();
  interview_how.setTitle("How would you rather do it?");
  interview_how.setChoiceValues(["Discord or Zoom", "Phone", "In person at an event", "Whatever is easiest for you"]);
  var interview_topics = form.addParagraphTextItem();
  interview_topics.setTitle("Anything you'd want to talk about \u2014 or anything to avoid?");
  interview_topics.setHelpText("A story you always tell, a year that mattered, someone who should get credit.");
  var interview_artifact = form.addParagraphTextItem();
  interview_artifact.setTitle("If you did one: what object would you bring?");
  interview_artifact.setHelpText("A card, a trophy, a receipt, a sleeve, a photo, a scar. It is the only part you get told about in advance, because choosing it is half the interview. No wrong answers, and you can change your mind.");

  form.addPageBreakItem().setTitle("Last thing");
  var anything = form.addParagraphTextItem();
  anything.setTitle("Anything we didn't ask that belongs on your page?");
  var email = form.addTextItem();
  email.setTitle("Email, in case we need to check something");
  var consent = form.addMultipleChoiceItem();
  consent.setTitle("Okay to publish these answers on teamserio.us?");
  consent.setChoiceValues(["Yes", "Yes, but check with me on the photo first", "Yes, but leave my last name off", "Ask me first"]);
  consent.setRequired(true);

  var ss = SpreadsheetApp.create('Team Serious \u2014 Bios (responses)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  Logger.log('Edit the form : ' + form.getEditUrl());
  Logger.log('Send this one : ' + form.getPublishedUrl());
  Logger.log('Responses     : ' + ss.getUrl());
}
