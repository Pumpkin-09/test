from dataclasses import dataclass, field
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

url_book_to_scrap = "http://books.toscrape.com"


@dataclass
class ListeCategories:

    liste_categories: list[str] = field(default_factory=list)
    

@dataclass 
class Livre:
    url: str 
    upc: str
    titre_livre: str 
    price_including_taxe: str 
    price_excluding_taxe: str
    number_available: str
    description_livre: str
    categorie_livre: str
    book_rating: str
    image_couverture: str


class LienLivresCategorie:

    def liste_livres(self, url):

        liste_pages = []
        liste_pages.append(url)
        page = requests.get(url)
        soupe = BeautifulSoup(page.content, "html.parser")
        pages = soupe.find("li", class_="next")
        while pages != None:
            nbr_page = pages.find.a.get("href")
            url_modifier = url.replace("index.html",nbr_page)
            liste_pages.append(url_modifier)
            page_modifier = requests.get(url_modifier)
            soupe = BeautifulSoup(page_modifier.content, "html.parser")
            pages = soupe.finf("li", class_="next")
        return liste_pages


@dataclass
class Scraping:
    url: str
    donnees_livre: list[str] = field(default_factory=list)

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
        upc = info_livre[0]
        price_including_taxe = info_livre[3]
        price_excluding_taxe = info_livre[2]
        number_available = info_livre[5]

        #Récuperation du titre
        titre = soup.find("h1")
        titre_livre = self.verification_donnees(titre.string)

        # Récuperation de la note du livre
        rating = soup.find("p", class_="star-rating")
        book_rating = TransformationDonnees().remplacement_note(rating["class"][-1])

        # Récupération du nom de la catégorie du livre
        categorie = soup.find("ul",class_="breadcrumb")
        cat = categorie.find_all("li")
        categorie_livre = self.verification_donnees(cat[2].text.strip())

        # Récupération de l'URL de l'image du livre
        image = soup.find("img")
        image_couverture = urljoin("http://books.toscrape.com/", image.get("src"))

        donnees_livre = Livre(
            self.url, 
            upc, 
            titre_livre, 
            price_including_taxe, 
            price_excluding_taxe, 
            number_available,
            description_livre,
            categorie_livre,
            book_rating,
            image_couverture
            )

            
    def verification_donnees(self, donnees):
        if donnees is None:
            donnees =  "Donnée non trouvée"
        return donnees




class TransformationDonnees:
    

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








livres = []
noms_categorie = []
liens_categorie = []
'''
# Créer le dossier "dossier livres" s'il n'existe pas déjà
dossier_livres = "dossier livres"
if not os.path.exists(dossier_livres):
    os.mkdir(dossier_livres)

# Créer le dossier "images" à l'intérieur du dossier "dossier livres" s'il n'existe pas déjà
dossier_images = os.path.join(dossier_livres, "images")
if not os.path.exists(dossier_images):
    os.mkdir(dossier_images)


page = requests.get(url_book_to_scrap)
soup = BeautifulSoup(page.content, "html.parser")
pages = soup.find("dinv", class_="side_categories")
infos_categories = pages.find("ul").find("li").find("ul")

# Récupération des noms des catégories
for nom_categories in infos_categories.children :
    if nom_categories.name :
        noms_categorie.append(nom_categories.text.strip())

# Récupération des liens des catégories
for lien_categories in infos_categories.find_all("a") :
    liens_categorie.append("https://books.toscrape.com/" + lien_categories.get("href"))
'''


for recup_lien in LienLivresCategorie().liste_livres(liens_categorie):
    page = requests.get(recup_lien)
    soupe = BeautifulSoup(page.content, "html.parser")
    links = soupe.find_all("article")
    for i in links:
        livres_d_une_categorie = Livre(i.h3.a.get("href").replace("../../..", "http://books.toscrape.com/catalogue"))
        livres.append(livres_d_une_categorie)
    
print(livres)




