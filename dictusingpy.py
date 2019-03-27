# import difflib
from difflib import get_close_matches as sq
import json
data = json.load(open("data.json"))


def find_word(word):
    word = word.lower()
    if word in data:
        return data[word]
    elif word.title() in data:
        return data[word.title()]
    elif word.upper() in data:
        return data[word.upper()]
    elif len(sq(word , data.keys())) > 0:
        yn = input("Did you mean %s instead? If yes input Y else input N " % sq(word, data.keys())[0])
        if yn == "Y":
            return data[sq(word, data.keys())[0]]
        elif yn == "N":
            return "The entered word isn't available in the dictionary"
        else:
            return "We did not understand your query."
    else:
        return "The entered word isn't available in the dictionary"


word = input("Enter a word: ")

w = find_word(word)
if type(w) == list:
    for i in w:
        print(i + "\n")
else:
    print(w)
