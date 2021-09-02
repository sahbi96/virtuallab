from googletrans import Translator
from bs4 import BeautifulSoup
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from nltk.tokenize import word_tokenize




def Tokenize_Text(k):
    wor_t = list(dict.fromkeys(word_tokenize(k))) 
    return wor_t


def Translate_Text(k):
    translator = Translator()
    tr =translator.translate(k,dest="en")
    return tr.text


def Extract_Text_From_Html(html):
    soup = BeautifulSoup(html, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()    

    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text



def Enrich_Formation(f):

    result = {"f_name":[],"f_full_desc":[],"f_short_desc":[]}
    result['f_name']=Tokenize_Text(Translate_Text(f.name))
    result['f_short_desc']=Tokenize_Text(Translate_Text(f.short_description))
    result['f_full_desc']=Tokenize_Text(Translate_Text(Extract_Text_From_Html(f.full_description)))
    return result



