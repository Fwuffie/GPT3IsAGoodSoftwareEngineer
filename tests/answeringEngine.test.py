import json, sys

# setting path
sys.path.append('.')

from answeringEngine import *

fSecrets = open("secrets.json", "r")
secrets = json.load(fSecrets)
fSecrets.close()

u = user(secrets["userInfo"])
e = answeringEngine(secrets["OpenAISecret"], u)

print("Tesing Classifier 1")
print(e.answerQuestion("What is your github?", "string"))
print("Tesing Classifier 2")
print(e.answerQuestion("What are your prefered pronouns?", "string"))
print("Tesing Bool and Function")
print(e.answerQuestion("Do you require visa sponsorship to work in the UK?", "bool"))
print("Tesing GPT String")
print(e.answerQuestion("What is your favorite Ice Cream?", "string"))
print("Tesing GPT Int")
print(e.answerQuestion("What is 4+3?", "int"))
print("Tesing GPT Bool")
print(e.answerQuestion("Is the moon a sphere?", "bool"))


