#! /usr/bin/python3.8
# coding: utf-8
import csv
import requests
from bs4 import BeautifulSoup
from pprint import pprint

# les listes
list_all_category = []
liens_produits = []

# Fonction qui récupère le lien de toutes les catégorie
def all_category():
    url = "http://books.toscrape.com"
    reponse = requests.get(url)
    soup = BeautifulSoup(reponse.text, "html.parser")
    i = 0
    url_category = soup.find("ul", {"class": "nav nav-list"}).findAll("a")
    for url in url_category:
        if i != 0:
            list_all_category.append("http://books.toscrape.com/" + url.get("href"))
        i += 1
    return list_all_category


# Fonctions qui récupère les liens de chaque livre d'une catégorie, en passant à la page suivante(si possible)
def scrap_1_category(category):
    reponse_lien_category = requests.get(category)
    soup = BeautifulSoup(reponse_lien_category.text, "html.parser")
    # récup liens produit (page1)
    product_url = soup.findAll("h3")
    for urls in product_url:
        a = urls.find("a")
        liens = a["href"][9:]

        liens_produits.append("http://books.toscrape.com/catalogue/" + liens)
    while soup.find("li", {"class": "next"}) is not None:
        # recupère le bouton next de chaque page
        bouton_next = soup.find("li", {"class": "next"}).find("a").get("href")
        url_bouton_next = category[:-10] + bouton_next
        # entre dans le bouton next (page suivante)
        reponse_page2 = requests.get(url_bouton_next)
        soup = BeautifulSoup(reponse_page2.text, "html.parser")
        # récup le reste des liens produits (page 2, 3 ...)
        product_url = soup.findAll("h3")
        for urls in product_url:
            a = urls.find("a")
            liens = a["href"][9:]
            liens_produits.append("http://books.toscrape.com/catalogue/" + liens)
    return liens_produits


# Fonction qui récupère les informations produits et télécharge les images
def infos_produits(lien):
    reponse_lien_prod = requests.get(lien)
    soup = BeautifulSoup(reponse_lien_prod.text, "html.parser")
    titre = soup.find("h1")
    scrap_image_url = soup.find("div", {"class": "item active"}).find("img")
    image_url = "http://books.toscrape.com" + scrap_image_url.get("src")[5:]
    alt_image = scrap_image_url.get("alt")
    info_table = [
        info.text
        for info in soup.find("table", {"class": "table-striped"}).findAll("td")
    ]
    # récupere uniquement la 4ème balise "p" et "a"
    description = soup.findAll("p")[3]
    category = soup.findAll("a")[3]
    table_list = []
    for info in info_table:
        table_list.append(info)
    recup_all_info = [
        lien,
        table_list[0],
        titre.text,
        table_list[2][1:],
        table_list[3][1:],
        table_list[5],
        description.text,
        category.text,
        table_list[6],
        image_url + " Tag: " + alt_image,
    ]
    # télécharge toutes les images dans un dossier, avec leurs nom
    dossier = b"images_download/" + str.encode(titre.text.replace("/", "_")) + b".jpg"
    r = requests.get(image_url, stream=True)
    with open(dossier, "wb") as jpg_test:
        jpg_test.write(r.content)
        pprint(titre.text)
    return recup_all_info, jpg_test


# Fonction qui télécharge les données dans un dossier csv différent pour chaques catégories
def csv_category(category):
    liste = scrap_1_category(category)
    print("Contient :", len(liste), "livres")
    nom = category[51:-11]
    dossier = "csv_category/"
    csv_columns = [
        "product_page_url",
        "universal_ product_code (upc)",
        "title",
        "price_including_tax",
        "price_excluding_tax",
        "number_available",
        "product_description",
        "category",
        "review_rating",
        "image_url",
    ]
    with open(dossier + nom + ".csv", "w", encoding="utf-8", newline="") as csv_file:
        write = csv.writer(csv_file)
        write.writerow(csv_columns)
        for lien in liste:
            infos = infos_produits(lien)
            write.writerow(infos)
    return liste




def main():
    i = 1
    for category in all_category():
        print("Categorie numero", i)
        csv_category(category)
        liens_produits.clear()
        i += 1


main()
