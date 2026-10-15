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
    'For the bios on teamserio.us. Only four questions are required \u2014 ' +
    'answer whatever else you feel like. One-word answers are a valid ' +
    'personality.\n\n' +
    'If you are signed in to a Google account it saves your progress as you ' +
    'go, so you can close the tab and pick it up later. You can also stop ' +
    'after the first few pages and submit what you have \u2014 there is a ' +
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
    'Got it \u2014 thank you.\n\n' +
    'Keep the link on this page if you want to edit your answers later, or ' +
    'just tell us and we will fix it. If you stopped early you can reopen ' +
    'the form any time to do the rest.');


  var page_who_you_are = form.addPageBreakItem().setTitle("Who you are").setHelpText("The part that ends up at the top of your page. Keep it short; the interesting stuff is further down.");
  var name = form.addTextItem();
  name.setTitle("Name, as you want it on the site");
  name.setRequired(true);
  var handle = form.addTextItem();
  handle.setTitle("Handle(s) \u2014 TMD, Discord, wherever you post");
  handle.setHelpText("So we can credit old posts and decklists to the right person.");
  var email = form.addTextItem();
  email.setTitle("Email");
  email.setHelpText("Only so we can check something, or sort out an interview time. Not published, not added to anything.");
  var where = form.addTextItem();
  where.setTitle("Where are you?");
  where.setHelpText("City and state is plenty. 'Leng' is also an accepted answer.");
  var photo = form.addFileUploadItem();
  photo.setTitle("A photo of you");
  photo.setHelpText("Playing, holding a trophy, or just a face. We can also pull one from an event report if you'd rather.");
  photo.setAllowedFileTypes([DriveApp.FileType.IMAGE]).setMaxFileSize(10);
  var day_job = form.addTextItem();
  day_job.setTitle("What do you do when you're not doing this?");
  var other_life = form.addParagraphTextItem();
  other_life.setTitle("Kids, pets, bands, other hobbies, anything you'd want mentioned");
  var links = form.addParagraphTextItem();
  links.setTitle("Anywhere you want linked");
  links.setHelpText("Podcast, YouTube, Bluesky, store, band. One per line.");

  var page_how_you_got_here = form.addPageBreakItem().setTitle("How you got here");
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

  var page_the_record = form.addPageBreakItem().setTitle("The record").setHelpText("Anything you want on the page as a credit. Modesty is not useful here, and neither is accuracy \u2014 if you think you won it, say you won it and we'll go and check.");
  var titles = form.addParagraphTextItem();
  titles.setTitle("Notable titles, nicknames, honorifics");
  titles.setHelpText("What people actually call you, who started it, and whether you accept it. Earned, inflicted and self-appointed all count.");
  var finishes = form.addParagraphTextItem();
  finishes.setTitle("Notable finishes?");
  finishes.setHelpText("Events, years, placings, as near as you remember. \"Second at something in Sandusky, I want to say 2016\" is a perfectly good answer \u2014 we have the write-ups and can pin it down.");
  var ts_events = form.addCheckboxItem();
  ts_events.setTitle("Which of ours have you been to?");
  ts_events.setHelpText("Tick anything you've played, not only ones you won.");
  ts_events.setChoiceValues(["TSI \u2014 The Land", "TSI \u2014 Mishra's By the Maumee", "TSI \u2014 Hazard Serious Invitational", "TSI \u2014 Kegerator Serious Invitational", "TSO \u2014 All-American Warren", "TSO \u2014 the POP! Shop", "Kumite", "Castmaster", "Middle School Intercontinental", "Ohio Ante something", "Others I have forgotten"]);
  var proudest = form.addParagraphTextItem();
  proudest.setTitle("The win you're proudest of, which may not be the biggest one");
  var beat = form.addParagraphTextItem();
  beat.setTitle("The loss you still think about");
  var underrated = form.addParagraphTextItem();
  underrated.setTitle("Who deserves more credit than they get?");
  underrated.setHelpText("Player, organiser, driver, person who always brings the food. We will probably quote you.");

  var page_the_20th_anniversary_interviews = form.addPageBreakItem().setTitle("The 20th anniversary interviews").setHelpText("For the anniversary we want to record a run of short \"life story\" interviews \u2014 about fifteen minutes each, two or three per episode, so nothing runs past half an hour. No prep and no wrong answers: how you found Magic, how you found us, one object you bring along, one story you always tell, and some rapid-fire nonsense. You finish by asking a question of whoever is up next, without knowing who that is.");
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
  var keep_going = form.addMultipleChoiceItem();
  keep_going.setTitle("That is everything we actually need. Keep going?");
  keep_going.setHelpText(
    "The rest is the fun half: the questionnaire, and the one about gas " +
    "station food. Stopping here still gives us a page, and you " +
    "can open the form again later to finish the rest.");
  keep_going.setRequired(true);

  var page_the_team_serious_questionnaire = form.addPageBreakItem().setTitle("The Team Serious questionnaire").setHelpText("The actual point of the exercise. Answer at whatever length you like; one-word answers are a valid personality.");
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
  var never_sleeve = form.addTextItem();
  never_sleeve.setTitle("A card you would never sleeve, on principle");
  var beat_up = form.addParagraphTextItem();
  beat_up.setTitle("Your most beat-up card, and why you won't replace it");
  var traded_away = form.addTextItem();
  traded_away.setTitle("Something you traded away that still stings");
  var ban_one = form.addTextItem();
  ban_one.setTitle("You may ban one card forever. Is the format grateful or furious?");
  var sleeves = form.addMultipleChoiceItem();
  sleeves.setTitle("Sleeves");
  sleeves.setChoiceValues(["Matte", "Glossy", "Whatever is in the bag", "I have strong feelings and will be sharing them"]);
  var heckle = form.addParagraphTextItem();
  heckle.setTitle("Best heckle you've given or taken");
  var rule_wrong = form.addTextItem();
  rule_wrong.setTitle("A rule you had wrong for years");
  var most_ts = form.addParagraphTextItem();
  most_ts.setTitle("The most Team Serious thing you have ever witnessed");
  most_ts.setHelpText("You do not have to name names. You may name names.");
  var hall_of_fame = form.addTextItem();
  hall_of_fame.setTitle("One thing \u2014 not a person \u2014 for the Team Serious hall of fame");
  var teach_one = form.addTextItem();
  teach_one.setTitle("You can teach someone one format. Which, and why that one?");

  var page_on_the_road = form.addPageBreakItem().setTitle("On the road").setHelpText("Half of this is the driving and the eating, and everybody knows it.");
  var radius = form.addMultipleChoiceItem();
  radius.setTitle("How far will you go for an event?");
  radius.setChoiceValues(["Across town", "A couple of hours", "Half a day's drive", "I will fly", "I have driven somewhere I should not have"]);
  var car_food = form.addTextItem();
  car_food.setTitle("What's in the car for a long drive?");
  var best_meal = form.addParagraphTextItem();
  best_meal.setTitle("Best meal on a Magic trip. Be specific \u2014 name the place.");
  best_meal.setHelpText("This is a legitimate historical record and will be treated as one.");
  var worst_venue = form.addParagraphTextItem();
  worst_venue.setTitle("Worst venue you've played in, and would you go back?");
  var gas_station = form.addTextItem();
  gas_station.setTitle("Defend one gas station food item");
  var travel_with = form.addTextItem();
  travel_with.setTitle("Who are you usually in the car with?");

  var page_last_thing = form.addPageBreakItem().setTitle("Last thing");
  var anything = form.addParagraphTextItem();
  anything.setTitle("Anything we didn't ask that belongs on your page?");
  var consent = form.addMultipleChoiceItem();
  consent.setTitle("Okay to publish these answers on teamserio.us?");
  consent.setChoiceValues(["Yes", "Yes, but check with me on the photo first", "Yes, but leave my last name off", "Ask me first"]);
  consent.setRequired(true);

  // Wired once every page exists: a choice cannot point at a page that has
  // not been created yet. "Stop here" skips to the final page so the form can
  // actually be submitted -- Forms has no part-way submit, and without this a
  // long form means people who give up leave nothing behind at all.
  keep_going.setChoices([
    keep_going.createChoice("Keep going", page_the_team_serious_questionnaire),
    keep_going.createChoice("Stop here \u2014 I will finish it later",
                            page_last_thing)
  ]);

  var ss = SpreadsheetApp.create('Team Serious — Bios (responses)');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  // One nudge, to people who chose to give an address, carrying the link
  // back into their own answers. See onBioSubmit below.
  ScriptApp.newTrigger('onBioSubmit').forForm(form).onFormSubmit().create();

  Logger.log('Edit the form : ' + form.getEditUrl());
  Logger.log('Send this one : ' + form.getPublishedUrl());
  Logger.log('Responses     : ' + ss.getUrl());
}

/**
 * Sends one email, once, with a link back into the person's own answers.
 *
 * This is why the form does not use Google's own "collect email" setting:
 * that makes an address compulsory for everyone. Here the address is an
 * ordinary optional question, and anyone who gives one gets a link they can
 * use to finish the rest whenever they like.
 *
 * ONCE is enforced with ScriptProperties. The submit trigger fires again when
 * someone edits an existing response, and nobody wants a fresh email every
 * time they fix a typo.
 */
function onBioSubmit(e) {
  var response = e.response;
  var address = null;
  var name = '';

  response.getItemResponses().forEach(function (item) {
    var title = item.getItem().getTitle();
    if (title === 'Email') {
      address = String(item.getResponse() || '').trim();
    }
    if (title === 'Name, as you want it on the site') {
      name = String(item.getResponse() || '').trim();
    }
  });

  if (!address || address.indexOf('@') < 0) { return; }

  var props = PropertiesService.getScriptProperties();
  var key = 'nudged:' + address.toLowerCase();
  if (props.getProperty(key)) { return; }

  var link = response.getEditResponseUrl();
  var hello = name ? (name.split(' ')[0] + ',') : 'Hello,';
  var nl = String.fromCharCode(10);

  MailApp.sendEmail({
    to: address,
    subject: 'Your Team Serious bio — the link back',
    body: hello + nl + nl +
      'Thanks for filling this in. Here is the link back to your own answers:' +
      nl + nl + link + nl + nl +
      'It reopens the form exactly as you left it, so you can finish the rest ' +
      'of the questions whenever you feel like it, or change anything you ' +
      'want back. Worth keeping — it is the only one you get, and we are ' +
      'not going to pester you again.' + nl + nl +
      'Team Serious' + nl
  });

  props.setProperty(key, new Date().toISOString());
}
