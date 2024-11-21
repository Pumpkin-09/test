import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import os

url_book_to_scrap = "http://books.toscrape.com"






    


class Livre:

    def __init__(self, url, upc, titre, price_including_taxe, price_excluding_taxe, number_available, description, categorie, book_rating, image_couverture):

        self.url = url
        self.upc = upc
        self.titre = titre
        self.price_including_taxe = price_including_taxe 
        self.price_excluding_taxe = price_excluding_taxe
        self.number_available = number_available
        self.description = description
        self.categorie = categorie
        self.book_rating = book_rating
        self.image_couverture = image_couverture
    
    def to_list(self):
        return [self.url, self.upc, self.titre, self.price_including_taxe, self.price_excluding_taxe, self.number_available, self.description, self.categorie, self.book_rating, self.image_couverture]


class Categorie:
    def __init__(self, nom):
        self.nom = nom

    def liste_de_livres(self, url_de_categorie):

        livres = []
        page = requests.get(url_de_categorie)
        soupe = BeautifulSoup(page.content, "html.parser")
        page_suivante = soupe.find("li", class_="next")
        while page_suivante != None:
            element_a = page_suivante.find("a")
            nbr_page = element_a.get("href")
            url_modifier = url_de_categorie.replace("index.html",nbr_page)

            page = requests.get(url_modifier)
            soupe = BeautifulSoup(page.content, "html.parser")
            liens_livre = soupe.find_all("article")
            for lien_livre in liens_livre:
                lien_livre_modifier = lien_livre.h3.a.get("href").replace("../../..", "http://books.toscrape.com/catalogue")
                livre = Scrapeur("truc").donnees_livre(lien_livre_modifier)
                livres.append(livre)

            page_modifier = requests.get(url_modifier)
            soupe = BeautifulSoup(page_modifier.content, "html.parser")
            page_suivante = soupe.find("li", class_="next")

        page = requests.get(url_de_categorie)
        soupe = BeautifulSoup(page.content, "html.parser")
        liens_livre = soupe.find_all("article")
        for lien_livre in liens_livre:
            lien_livre_modifier = lien_livre.h3.a.get("href").replace("../../..", "http://books.toscrape.com/catalogue")
            livre = Scrapeur("livre").donnees_livre(lien_livre_modifier)
            livres.append(livre)

        return livres



class Scrapeur:
    def __init__(self, nom):
        self.nom = nom

    def donnees_livre(self, url):
        
        page = requests.get(url)
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

        donnees_du_livre = Livre(
            url, 
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
        liste_donnees_livre = donnees_du_livre.to_list()
        return liste_donnees_livre

            
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





def ecriture_donnees_livres(nom, dossier_livres, dossier_images, donnees) :
    # Enregistrement des données dans un fichier CSV nommé en fonction de la catégorie.
    en_tete = ["product_page_url", "universal_product_code (upc)", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating","image_url","nom_image", "chemin_image"]

    for liste_donnees_livres in donnees:
        name = os.path.join(dossier_livres, nom +".csv")
        with open(name, "w", encoding = "utf-8") as f :
            writer = csv.writer(f, delimiter = ",")
            writer.writerow(en_tete)
            writer.writerow(liste_donnees_livres)

    #Téléchargement de l'image dans le dossier "images"
    #L'image est également renomé en fonction du nom du livre.
    
        nom_image = liste_donnees_livres[1]
        chemin_image = os.path.join(dossier_images, nom_image)
        f = open(chemin_image, "wb")

        
        response = requests.get(liste_donnees_livres[9])
        f.write(response.content)
        f.close()


def recuperation_des_donnees(url):

    # Créer le dossier "dossier livres" s'il n'existe pas déjà
    dossier_livres = "dossier livres"
    if not os.path.exists(dossier_livres):
        os.mkdir(dossier_livres)

    # Créer le dossier "images" à l'intérieur du dossier "dossier livres" s'il n'existe pas déjà
    dossier_images = os.path.join(dossier_livres, "images")
    if not os.path.exists(dossier_images):
        os.mkdir(dossier_images)

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    pages = soup.find("div", class_="side_categories")
    infos_categories = pages.find("ul").find("li").find("ul")

    # Récupération des noms des catégories
    noms_categorie = []
    for nom_categories in infos_categories.children :
        if nom_categories.name :
            noms_categorie.append(nom_categories.text.strip())

    # Récupération des liens des catégories
    liens_categorie = []
    for lien_categories in infos_categories.find_all("a") :
        liens_categorie.append("https://books.toscrape.com/" + lien_categories.get("href"))

    for nom_categorie,lien_categorie in zip(noms_categorie, liens_categorie):
        donnees_des_livres = Categorie(nom_categorie).liste_de_livres(lien_categorie)
        ecriture_donnees_livres(nom_categorie, dossier_livres, dossier_images, donnees_des_livres)








recuperation_des_donnees(url_book_to_scrap)






