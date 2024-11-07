from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging


@dataclass
class Categorie:
    url: str

    def pages_total_categorie(url):
        url_list = []
        url_list.append(url)
        page = requests.get(url)
        soupe = BeautifulSoup(page.content, "html.parser")

        pages = soupe.find("li", class_="next")
        while pages != None:
            nbr_page = pages.find.a.get("href")
            url_modifier = url.replace("index.html",nbr_page)
            url_list.append(url_modifier)
            page_modifier = requests.get(url_modifier)
            soupe = BeautifulSoup(page_modifier.content, "html.parser")
            pages = soupe.finf("li", class_="next")
        return url_list


@dataclass
class Livre:
    product_page_url: str
    upc: str
    title: str
    price_including_taxe: str
    price_excouding_taxe: str
    number_available: str
    product_description: str
    category: str
    review_rating: str
    image_url: str


    def scrap(self, url):
        self.url = url
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        links_books = soup.find_all("article")
        for i in links_books:
            link = (i.h3.a.get("href").replace("../../..", "http://books.toscrape.com/catalogue"))
            page = requests.get(link)
            soup = BeautifulSoup(page.content, "html.parser")

            # Récupération de la description du livre
            description = soup.find("div", class_="sub-header")
            description_livre = self.verificaiton_donnees(description.find_next("p").string)

            # Récupération du UPC, des prix et du nombre en stock
            info_livre = []
            infos = soup.find_all("td")
            for info in infos:
                info_livre.append(info.string)

            #Récuperation du titre
            titre = soup.find("h1")
            titre_livre = self.verification_donnees(titre.string)

            # Récuperation de la note du livre
            rating = soup.find("p", class_="star-rating")
            book_rating = self.verification_donnees(rating["class"][-1])

            # Récupération du nom de la catégorie du livre
            categorie = soup.find("ul",class_="breadcrumb")
            cat = categorie.find_all("li")
            categorie_livre = self.verification_donnees(cat[2].text.strip())

            # Récupération de l'URL de l'image du livre
            image = soup.find("img")
            image_couverture = urljoin("http://books.toscrape.com/", image.get("src"))

            


    def verification_donnees(self, donnees):
        if donnees is None:
            donnees =  "Donnée non trouvée"
        return donnees

    def remplacement_note(self, note):
        remplacement = {
        "One" : "1 sur 5",
        "Two" : "2 sur 5",
        "Three" : "3 sur 5",
        "Four" : "4 sur 5",
        "Five" : "5 sur 5"
        }
        if note in remplacement:
            note_chiffre = remplacement[note]
        else:
            note_ciffre = "note non valide"

        return(note_ciffre)








