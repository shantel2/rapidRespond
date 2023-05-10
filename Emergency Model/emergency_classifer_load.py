import joblib
import re
import string

from nltk.stem import WordNetLemmatizer

from sklearn.feature_extraction.text import CountVectorizer

categories = ['Fire','Police','Medical']

#Process Text

def process_text(text):
    text = str(text).lower()
    text = re.sub(
        f"[{re.escape(string.punctuation)}]", " ", text
    )
    text = " ".join(text.split())
    return text

vec = CountVectorizer(
    ngram_range=(1, 3), 
    stop_words="english",
)

lemmatizer = WordNetLemmatizer()
def lemmatize_text(word):
    def lemmatizeHelper(text):
        return lemmatizer.lemmatize(text)
    word_filtered = process_text(word)
    word_lst = []
    for word in word_filtered.split():
        word_lst += [lemmatizeHelper(word)]
    
    return " ".join(word_lst)

nb_saved = joblib.load("emergency_nb.joblib") #loads model
vec_saved = joblib.load("emegency_vec.joblib") #loads vectoriser

def predict_emergency(text):
    sample_text = [text] #takes input
    clean_sample_text = [lemmatize_text(sample_text)] #lceans up given text, lemmatises it
    sample_vec = vec_saved.transform(clean_sample_text) #transforms text to vector based on vectoriser
    print(categories[nb_saved.predict(sample_vec)[0]]) #determines category using model

predict_emergency(input())