import spacy
import arrow
import dateparser

spacy_nlp = spacy.load("en_core_web_lg")


date_strings = ["Ratified Indian Treaty 18:  Cherokee - Holston River with additional article of February 17, 1792 at Philadelphia",
"Ratified Indian Treaty 19A:  Six Nations - New York, April 19, 1793",
"Ratified Indian Treaty 22:  Oneida, Tuscarora, and Stockbridge - Oneida, New York, December 2, 1794"]

filename = "/Users/matt.mcgrattan/Documents/Github/ida_treaty_explorer/ida_treaty_explorer/hello/data/List of Indian_Treaties.csv"

with open(filename, "r") as f:
    t = f.readlines()
    date_strings = [x.split("|")[1].strip() for x in t]



for d_string in date_strings:
    doc = spacy_nlp(d_string)
    poss_dates = [e.text for e in doc.ents if e.label_ == "DATE"]
    if not any(["," in x for x in poss_dates]):
        poss_date_strings = [",".join(poss_dates)]
    else:
        poss_date_strings = poss_dates
    print(f"String: {d_string}")
    dates = [dateparser.parse(poss_date_string) for poss_date_string in poss_date_strings]
    print(f"Dates: {dates}")