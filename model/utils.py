
from enum import Enum
import re
import nltk
import numpy as np
from nltk import word_tokenize
from nltk.corpus import stopwords

nltk.download('stopwords')
nltk.download('punkt')

def get_stop_words():
    stop_words_tr = stopwords.words("turkish")
    with open('turkce-stop-words.txt', encoding="utf-8") as f:
        lines = f.read().splitlines()

    new_words = list()
    # Strips the newline character
    for line in lines:
        new_words.append(line)
    
    stop_words_tr.extend(new_words)

    return np.unique(np.array(stop_words_tr)).tolist()


def clean_text(x):
    x = str(x)
    x = x.lower()
    x = re.sub(r'#[A-Za-zğüşıöçĞÜŞİÖÇ0-9-_]*', '', x, flags=re.IGNORECASE | re.UNICODE)
    x = re.sub(r'https*://.*', '', x)
    x = re.sub(r'@[A-Za-zğüşıöçĞÜŞİÖÇ0-9-_]+', '', x, flags=re.IGNORECASE | re.UNICODE)
    tokens = word_tokenize(x)
    x = ' '.join([w for w in tokens if not w.lower() in get_stop_words()])
    x = re.sub(r'[%s]' % re.escape('!"#$%&\()*+,-./:;<=>?@[\\]^_`{|}~“…”’'), ' ', x)
    x = re.sub(r'\d+', ' ', x)
    x = re.sub(r'\n+', ' ', x)
    x = re.sub(r'\s{2,}', ' ', x)
    return x


class RetValue(Enum):
    TotalTweetCountIsEnough = 2,
    TotalTweetCountIsNotEnough = 3,
    EarlyRequestFail = 5,
    Success = 0,
    Fail = 1


class EarlyRequestException(Exception):

    # Constructor or Initializer
    def __init__(self, value):
        self.value = value

    # __str__ is to print() the value
    def __str__(self):
        return (repr(self.value))