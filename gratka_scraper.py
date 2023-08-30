import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import requests
from PIL import Image
from io import BytesIO
import json
import re
from tqdm import tqdm


class GratkaScraper:
    def __init__(self):
        pass

    def __get_offers_urls(self, page_id):
        """Zwraca adresy URL ofert z strony o numerze page_id"""
        URL = f"https://gratka.pl/nieruchomosci/mieszkania/wynajem?page={page_id}"
        response = requests.get(URL)

        if response.status_code == 200:
            response_parsed = BeautifulSoup(response.text, "html.parser")
            print(f"Zawartość strony {page_id} została pobrana")

            listing_elements = response_parsed.find_all(class_="teaserLink")
            urls = [url["href"] for url in listing_elements]

            return urls

        else:
            print(f"Wystąpił błąd podczas pobierania zawartości strony {page_id}.")

    def __get_descriptions(self, urls):
        """Zwraca listę opisów ofert z podanych adresów URL"""
        descriptions = []
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                response_parsed = BeautifulSoup(response.text, "html.parser")
                description = (
                    response_parsed.find(class_="description__rolled ql-container")
                    .get_text()
                    .strip()
                )
                description = description.replace("+48...", "")
                description = description.replace("pokaż numer", "")
                description = description.replace("\n", "")
                descriptions.append(description)

            else:
                print("Wystąpił błąd podczas pobierania opisu")

        return descriptions

    def description_scrapper(self, pages_from, pages_to):
        """Zwraca ramkę danych zawierającą opisy ofert z podanego zakresu stron"""
        df = pd.DataFrame(columns=["Label"])

        for page_id in range(pages_from, pages_to + 1):
            offers_urls = self.__get_offers_urls(page_id)
            descriptions = self.__get_descriptions(offers_urls)
            for description in descriptions:
                df_to_append = pd.DataFrame({"Opis": [description]})
                df = pd.concat([df, df_to_append], ignore_index=True)

        return df

    def __get_images_urls(self, offers_urls):
        """Zwraca listę adresów URL zdjęć z podanych adresów URL ofert"""
        image_urls = []

        for url in offers_urls:
            offer = []
            response = requests.get(url)
            if response.status_code == 200:
                response_parsed = BeautifulSoup(response.text, "html.parser")
                gallery = response_parsed.find(class_="offer__relativeBox").find(
                    "script"
                )

                pattern = r"dataJson: (\[[^\]]+\])"
                match = re.search(pattern, gallery.text)

                if match:
                    data_json_str = match.group(1)
                    data_json_str = data_json_str.replace("\\", "")
                    data_json_str += "}]"
                    data_json = json.loads(data_json_str)[0]

                    for data in data_json["data"]:
                        offer.append(data["url"])

                    image_urls.append(offer)

                else:
                    print("dataJson nie znaleziony w tagu Script")

            else:
                print("Wystąpił błąd podczas pobierania adresów URL")

        return image_urls

    def __get_images(self, images_urls, save_path, img_shape=None):
        for i, offer in enumerate(tqdm(images_urls, desc=f"Postęp pobierania obrazów")):
            for j, url in enumerate(offer):
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    image = Image.open(BytesIO(response.content))

                    if img_shape is not None:
                        image = image.resize(img_shape)

                    image_extension = os.path.splitext(url)[-1].split("?")[0]

                    image_path = save_path + f"/{i}"

                    if not os.path.exists(image_path):
                        os.makedirs(image_path)

                    image.save(save_path + f"/{i}/" + f"image_{j}{image_extension}")

                except Exception as e:
                    print(f"Nie udało się pobrać i zapisać zdjęcia {i+1}: {e}")

    def image_scrapper(self, pages_from, pages_to, save_path, img_shape=None):
        """
        Zapisuje w określonym katalogu obrazy z ofert na podstawie podanego zakresu stron.
        Obrazy z każdej oferty zapisywane są w osobnym katalogu.
        """

        images_urls = []
        for page_id in range(pages_from, pages_to + 1):
            if not os.path.exists(save_path + f"/{page_id}"):
                os.makedirs(save_path + f"/{page_id}")

            offers_urls = self.__get_offers_urls(page_id)
            images_urls = self.__get_images_urls(offers_urls)

        self.__get_images(images_urls, save_path, img_shape)
