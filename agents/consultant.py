import os
from path import promptsDir
from models.generation import GenerationModel

class Consultant:
    def __init__(self):
        consultantAgent = GenerationModel(os.path.join(promptsDir, "consultant.md"))
        
    def askQuestion(self, query: str):
        pass 

    def generateReport(self, conversation: str):
        pass