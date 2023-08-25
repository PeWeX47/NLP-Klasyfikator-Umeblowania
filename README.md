# NLP-Klasyfikacja-Umeblowania-Mieszkan

Ten projekt ma na celu zastosowanie technik analizy tekstu oraz uczenia maszynowego do klasyfikacji umeblowania mieszkań na podstawie opisów mieszkań do wynajęcia z serwisu gratka.pl. Projekt wykorzystuje język Python do budowy modelu klasyfikacji.

## Instalacja

1. Sklonuj to repozytorium na swoje urządzenie:

``` bash
git clone git@github.com:PeWeX47/NLP-Klasyfikacja-tekstu-Umeblowanie-mieszkan.git
```

2. Zainstaluj niezbędne biblioteki z pliku requirements.txt, korzystając z polecenia:
``` cmd
pip install -r requirements.txt
```

3. Przed zainstalowaniem bibliotek zalecane (*ale nie wymagane*) jest użycie środowiska wirtualnego w celu izolacji zależności projektu. Jeśli nie masz zainstalowanego narzędzia virtualenv, możesz je zainstalować przy użyciu polecenia:
``` cmd
pip install virtualenv
``` 
- Stwórz nowe środowisko wirtualne:
``` cmd
python -m venv venv
```

- Aktywuj środowisko wirtualne:
``` cmd
venv\Scripts\activate.bat
```

## Scraping danych
Aby pobrać opisy lub zdjęcia mieszkań ze strony gratka.pl, możesz skorzystać z klasy GratkaScraper dostarczonej w pliku scraper.py. Poniżej znajduje się przykład użycia tej klasy (*zalecany jupyter notebook*):

``` py
from gratka_scraper import GratkaScraper
import pandas as pd
import matplotlib.pyplot as plt
import cv2

# scrapowanie opisów
scrapper = GratkaScraper()
df = scrapper.description_scrapper(pages_from=1, pages_to=2)

# scrapowanie obrazów 
scrapper.image_scrapper(pages_from=1, pages_to=2,
save_path=r'<scieżka do katalogu w którym chcemy zapisać obrazy>')
```

Proces scrapowania przedstawiony jest dokładniej w notatniku *scraping_test.ipynb*

## Wstępne przygotowanie danych
Proces wyboru danych treningowych oraz ich etykietowania przedstawiony jest w notatniku *data_selection.ipynb*
<br>
Ręcznie poprawione etykiety znajdują się w katalogu *data\descriptions\training_data_recznie_poprawione.csv*. Zbiór zawiera:

- 259 opisów mieszkań nieumeblowanych (*etykieta 0*)
- 235 opisów mieszkań umeblowanych (*etykieta 1*)
- 273 opisy mieszkań częsciowo umeblowanych (*etykieta 2*)

## Przetwarzanie danych i modelowanie
Kod odpowiedzialny za przetwarzanie danych oraz budowę modelu klasyfikacji znajduje się w notatniku *model_training.ipynb*
<br>
Wykorzystane zostały 3 metody wektoryzacji tekstu:

- TF-IDF Vectorizer
- Count Vectorizer
- Count Vectorizer z wykorzystaniem bigramów

Dla każdej z metod wektoryzacji wytrenowano modele:
- Maszyny Wektorów Nośnych
- Drzewa Decyzyjnego
- Lasów Losowych
- Regresji Logistycznej

Przykładowe wykorzystanie modelu dla pojedyńczego opisu mieszkania:
- Deklaracja funkcji *one_sample_predict*
``` py
def one_sample_predict(model, train_data):
    """ Funkcja przyjmuje wytrenowany model oraz jego dane treningowe w postaci tekstowej. 
    Pobiera od użytkownika pojedyńczy opis przetwarzając go i zwracając predykcję """
    text = input("Podaj opis: ")
    tfidf = TfidfVectorizer(max_features=80)
    _ = tfidf.fit_transform(train_data)
    classes = ["nieumeblowane", "umeblowane", "częściowo umeblowane"]
    text = text.lower()
    cleaned_text = re.sub("\d+", "", text)
    cleaned_text = re.sub(r"http\S+", "", cleaned_text)
    cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)

    doc = nlp(cleaned_text)
    cleaned_text = " ".join([token.lemma_ for token in doc if not token.is_stop])

    cleaned_text = re.sub(r"\b\w\b\s*", "", cleaned_text)
    vectorized_text = tfidf.transform([cleaned_text])

    pred = model.predict(vectorized_text)
    return classes[pred[0]]

```

- Przykładowe wywyołanie funkcji *one_sample_predict*

``` py
one_sample_predict(svm_clf, X_train)
Przykładowy output: 'częściowo umeblowane'
```

