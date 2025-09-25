decks = js["Decks"]

for deck in decks:
    print(deck["Player"])
    print("Mainboard")
    for card in deck["Mainboard"]:
        print(str(card["Count"]) + " " + card["CardName"])
    print("")
    print("Sideboard")
    for card in deck["Sideboard"]:
        print(str(card["Count"]) + " " + card["CardName"])
    print("")