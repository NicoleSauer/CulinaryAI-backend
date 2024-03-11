from bs4 import BeautifulSoup
from urllib.request import urlopen
from collections import defaultdict
import json
from datetime import datetime

my_id = 0
recipes = []
main_dataset_json = []


def scrape_all_links(recipes):
    for i in range(24): # 24 == Anzahl der Seiten
        page = urlopen(f"https://www.chefkoch.de/rs/s{i}t211/Studentenkueche-Rezepte.html").read()

        soup = BeautifulSoup(page, "html.parser")

        recipe_links = [link.get("href") for link in soup.find_all("a") if "https://www.chefkoch.de/rezepte/" in link.get("href")]  
        re_recipe_links = [recipe for recipe in recipe_links if len(recipe) > 52]

        recipes += re_recipe_links

    print(f"Links wurden geladen: {len(recipes)}")


def build_dict_for_ingredients(ing_name, ing_amount, ing_unit):
    ingrendiets_dict = defaultdict(dict)
    ingrendiets_dict["name"] = ing_name
    ingrendiets_dict["amount"] = ing_amount
    ingrendiets_dict["unit"] = ing_unit
    return ingrendiets_dict


def build_dict(chefkoch_id, recipe_link, title, ingredients, instructions, day, month, year, weekday, average_rating, num_rating, prep_time, difficulty_level, tags, number_of_portions, nutritional_values):
    global my_id
    new_dict = defaultdict(dict)
    new_dict["ID"] = my_id
    new_dict["chefkochID"] = chefkoch_id
    new_dict["link"] = recipe_link
    new_dict["name"] = title
    new_dict["ingredients"] = ingredients
    new_dict["instructions"] = instructions
    new_dict["day"] = day
    new_dict["month"] = month
    new_dict["year"] = year
    new_dict["weekday"] = weekday
    new_dict["averageRating"] = average_rating
    new_dict["numRating"] = num_rating
    new_dict["prepTime"] = prep_time
    new_dict["difficultyLevel"] = difficulty_level
    new_dict["tags"] = tags
    new_dict["numberOfPortions"] = number_of_portions
    new_dict["nutritionalValues"] = nutritional_values

    main_dataset_json.append(new_dict)
    print(f"{my_id}: Dict für Rezept wurde angelegt")
    my_id += 1


def scrape_recipe(recipes):
    global my_id
    for recipe_link in recipes:
        page = urlopen(recipe_link)
        soup = BeautifulSoup(page, "html.parser")

        # Chefkoch ID extrahieren
        try:
            chefkoch_id = recipe_link.split("/")[4]
        except:
            chefkoch_id = None

        # Name des Gerichts extrahieren
        try:
            title = soup.find("h1").text
        except:
            title = None

        # Die Zutate des Gerichts extrahieren
        try:
            raw_ingredients = [" ".join(i.text.split()) for i in soup.find_all("td")]

            ing_names = [i for i in raw_ingredients[1::2]]
            ing_details = [i for i in raw_ingredients[::2]]

            ing_amounts = []
            ing_units = []

            for detail in ing_details:
                try:
                    ing_amounts.append(int(detail.split()[0]))
                except:
                    ing_amounts.append(None)

                try:
                    ing_units.append(detail.split()[1])
                except:
                    ing_units.append(None)

            ingredients = []
            for name, amount, unit in zip(ing_names, ing_amounts, ing_units):
                ingredients.append(build_dict_for_ingredients(name, amount, unit))
        except:
            ingredients = []

        # Die Kochanweisung extrahieren
        try:
            recipe_instructions = soup.find_all("h2")
            recipe_h2 = recipe_instructions[2].text

            if recipe_h2 == "Zubereitung":
                recipe_instr_header = recipe_instructions[2]
            else:
                recipe_instr_header = recipe_instructions[1]

            recipe_instr = " ".join(recipe_instr_header.parent.findNext("div", {"class": "ds-box"}).text.split())
            
        except:
            recipe_instr = None

        # Den Tag des Reteptes extrahieren
        try:
            day = soup.find("span", {"class": "recipe-date"}).text.split()[1][:2]
        except:
            day = None

        # Den Monat des Reteptes extrahieren
        try:
            month = soup.find("span", {"class": "recipe-date"}).text.split()[1][3:5]
        except:
            month = None

        # Das Jahr des Reteptes extrahieren
        try:
            year = soup.find("span", {"class": "recipe-date"}).text.split()[1][6:10]
        except:
            year = None

        # Den Wochentag des rezetes extrahieren
        try:
            weekday = soup.find("span", {"class": "recipe-date"}).text.split()[1]
            days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"] 
            date = datetime(int(weekday[6:]), int(weekday[3:5]), int(weekday[:2]))
            true_weekday = days[date.weekday()]
        except:
            true_weekday = None

        # Das durchschnitliche Rating extrahieren
        try:
            avg_rating = float(soup.find("div", {"class": "ds-rating-avg"}).text.split()[2])
        except:
            avg_rating = None
        
        # Die Anzahl der Ratings extrahieren
        try:
            num_rating = int(soup.find("div", {"class": "ds-rating-count"}).text.split()[0][1:].replace(".", ""))
            if num_rating != 0:
                num_rating = int(soup.find("div", {"class": "ds-rating-count"}).text.split()[0][1:].replace(".", ""))
            else:
                num_rating = None
                avg_rating = None
        except:
            num_rating = None
        
        # Die Zubereitungsdauer extrahieren
        try:
            prep_time = int(soup.find("span", {"class": "recipe-preptime"}).text.split()[1])
        except:
            prep_time = None

        # Den Schwierigkeitsgrad extrahieren
        try:
            dif_level = soup.find("span", {"class": "recipe-difficulty"}).text.split()[1]
        except:
            dif_level = None

        # Die Tags des Rezeptes extrahieren
        try:
            recipe_tags = soup.find("div", {"class": "recipe-tags"}).text.split()
        except:
            recipe_tags = None

        # Die Anzahl der Protionen extrahieren
        try:
            recipe_portions = soup.find_all(attrs={"aria-label":"Anzahl der Portionen"})
            recipe_portion = int(recipe_portions[0]["value"])
        except:
            recipe_portion = None
        
        # Die Nährwerte eines Rezeptes extrahieren
        try:
            nutritional_values = soup.find("div", {"class": "recipe-nutrition_content"}).text.split()
            nutri_dict = defaultdict(dict)
            nutri_dict["kcal"] = float(nutritional_values[1])
            nutri_dict["protein"] = float(nutritional_values[3].replace(",", "."))
            nutri_dict["fat"] = float(nutritional_values[6].replace(",", "."))
            nutri_dict["carbonhydrates"] = float(nutritional_values[9].replace(",", "."))
        except:
            nutri_dict = defaultdict(dict)
            nutri_dict["kcal"] = None
            nutri_dict["protein"] = None
            nutri_dict["fat"] = None
            nutri_dict["carbonhydrates"] = None
            #print("Nährwerte nicht vorhanden")
            
        # Genrierung des Dictionaries von dem Rezept
        build_dict(chefkoch_id=chefkoch_id,
                   recipe_link=recipe_link, 
                   title=title, 
                   ingredients=ingredients, 
                   instructions=recipe_instr, 
                   day=day, month=month, 
                   year=year, 
                   weekday=true_weekday, 
                   average_rating=avg_rating, 
                   num_rating=num_rating, 
                   prep_time=prep_time, 
                   difficulty_level=dif_level, 
                   tags=recipe_tags, 
                   number_of_portions=recipe_portion, 
                   nutritional_values=nutri_dict
                   )
        

def write_json(main_dataset_json):
    with open("chefkoch_recipes_DB_test.json", "w", encoding="utf-8") as f:
        json.dump(main_dataset_json, f, indent=4)
        f.close()
    print("JSON wurde erstellt.")
        

    

scrape_all_links(recipes)

scrape_recipe(recipes)

write_json(main_dataset_json)




"""
TODO:
- Die daten nach versciedenen Kriterien filtern
"""