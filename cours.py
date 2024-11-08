from dataclasses import dataclass
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import logging








@dataclass
class Scraping:
    url: str
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

    def __post_init__(self):
        
        page = requests.get(self.url)
        soup = BeautifulSoup(page.content, "html.parser")

        # Récupération de la description du livre
        description = soup.find("div", class_="sub-header")
        description_livre = self.verification_donnees(description.find_next("p").string)

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
        book_rating = self.remplacement_note(rating["class"][-1])

        # Récupération du nom de la catégorie du livre
        categorie = soup.find("ul",class_="breadcrumb")
        cat = categorie.find_all("li")
        categorie_livre = self.verification_donnees(cat[2].text.strip())

        # Récupération de l'URL de l'image du livre
        image = soup.find("img")
        image_couverture = urljoin("http://books.toscrape.com/", image.get("src"))

        self.url
        self.upc = info_livre[0]
        self.title = titre_livre
        self.price_including_taxe = info_livre[3]
        self.price_excluding_taxe = info_livre[2]
        self.number_available = info_livre[5]
        self.product_description = description_livre
        self.category = categorie_livre
        self.review_rating = book_rating
        self.image_url = image_couverture

            
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
            note_chiffre = "note non valide"

        return(note_chiffre)









