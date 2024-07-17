from cs50 import get_string

text = get_string("Text: ")

def count_letters(text):
    x = 0
    for i in text:
        if i.isalpha():
            x += 1
    return x

def count_words(text):
    x = 1
    for i in text:
        if i == " ":
            x += 1
    return x

def count_sentences(text):
    x = 0
    ends = [".", "!", "?"]
    for i in text:
        if i in ends:
            x += 1
    return x

letters = count_letters(text)

words = count_words(text)

sentences = count_sentences(text)

l = (float(letters) / float(words)) * 100
s = (float(sentences) / float(words)) * 100
cl_index = (0.0588 * l) - (0.296 * s) - 15.8
r = round(cl_index)

if r >= 16:
    print("Grade 16+")
elif r < 1:
    print("Before Grade 1")
else:
    print(f"Grade {r}")