import os
from path import promptsDir
from models.generation import GenerationModel

consultantAgent = GenerationModel(os.path.join(promptsDir, "consultant.md"))

consultationHistory = []
while True:
    userInput = input("You: ")
    response = consultantAgent.generate(query=userInput, history=consultationHistory)
    if response == "Ready to Proceed!":
        break
    print(f"Bot: {response}")

print("Okay, Our consultation is over!")