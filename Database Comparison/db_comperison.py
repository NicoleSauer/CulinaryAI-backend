import pymongo
import textwrap

myclient = pymongo.MongoClient("mongodb://localhost:27017/")

mydb = myclient["RecipesChefKoch"]
mycol = mydb["ScrapedRecipes"]

menu = ("""
1. Zutaten eingeben
2. Beenden
""")

user_recipes = []

while True:

    user_input = int(input(menu))

    if user_input == 1:

        user_ingridients = input("What ingredients do you have?: ").lower().split()
        myquery = {"ingredients.name": {"$in": user_ingridients}}
        mydoc = mycol.find({})

        for doc in mydoc:
            for name in doc['ingredients']:
                for user_input in user_ingridients:
                    if user_input in name['name']:
                        user_recipes.append(doc)

        for index, recipe in enumerate(user_recipes):
            print(f"[{index}] - {recipe['name']}")
    
        choice = int(input("Which recipe: "))

        recipe_name = user_recipes[choice]['name']
        recipe_ingregdients = user_recipes[choice]['ingredients']
        recipe_instructions = user_recipes[choice]['instructions']

        print("|----------------------------------------------------------------------------------")
        print(f"| Name: {recipe_name}")
        print("|")
        print("| Ingredients:")
        for i in recipe_ingregdients:
            if i['amount'] == None:
                print(f"|    - {i['name']}")
            elif i['unit'] == None:
                print(f"|    - {i['name']} | {i['amount']}")
            else:
                print((f"|    - {i['name']} | {i['amount']} {i['unit']}"))
        print("|")
        print("| Instructions:")
        print(textwrap.fill(recipe_instructions, width=80, initial_indent="| ", subsequent_indent="| "))
        print("|----------------------------------------------------------------------------------")

        user_recipes.clear()

    elif user_input == 2:
        break

    else:
        print("Ungültige Eingabe")


'''
Ein Nachteil der Datenbank, welcher möglich ist (war vorhanden):
- "birne" wird nicht gefunden, obwohl sie als Zutat mit einem Rezept existiert
-> Schuld daran ist, dass birne als Birne(n) gespeichert ist. Somit kann die Datenbankanwendung es nicht finden, wenn es nur nach "birne" sucht.

Im Gegensatz zur einer KI-Anwendung, ist eine Datenbankanwendung sehr regelbasiert!
'''