import Levenshtein
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from .utils import takeClosestNumber

class QueryParser:
    stop_words = set(stopwords.words('english')) 

    stop_words.update(["years", "experience", "fully", ".", ",", "capability", "capacity", "proficiency", "able", "hold", "level"])

    fluencyDict = {"conversational", "reading", "fluent", "fully-fluent"}

    experienceDict = {1: "1-plus-year", 2: "2-plus-years", 3: "3-plus-years", 5: "5-plus-years", 10: "10-plus-years"}

    #Limitations: no potential to develop
    def getPairings(self, text):
    
        word_tokens = word_tokenize(text)

        filtered_sentence = [w for w in word_tokens if not w in self.stop_words] 

        resultList = []

        experience = None
        term = ""
        fluency = None 

        for word in filtered_sentence:

            #If it is a digit, then it probably is experience
            if word.isdigit():

                #see if an item is completed (skill with experience or language with fluency)
                experience, term, fluency, wordResultDict = self.dictIfCompletedItem(experience, term, fluency)
                resultList.extend(wordResultDict)
                experience = int(word)

            #if a word is in the fluency dictionary, then it is used as fluency
            elif word in self.fluencyDict:
                #see if an item is completed (skill with experience or language with fluency)
                experience, term, fluency, wordResultDict = self.dictIfCompletedItem(experience, term, fluency)
                resultList.extend(wordResultDict)
                fluency = word
            else:
                
                #check Levenshtein distance to see if a word is included in the fluency dictionary
                for fluencyFromSet in self.fluencyDict:
                    if Levenshtein.distance(fluencyFromSet, word) < 3:
                        #see if an item is completed (skill with experience or language with fluency)
                        experience, term, fluency, wordResultDict = self.dictIfCompletedItem(experience, term, fluency)
                        resultList.extend(wordResultDict)
                        fluency = fluencyFromSet

                        word = ""


                #if none of the above are true, then it must be part of a skill or the skill itself
                term += (" " + word)

        #see if any items left are completed 
        _, _, _, wordResultDict = self.dictIfCompletedItem(experience, term, fluency)
        resultList.extend(wordResultDict)
        return resultList

    def dictIfCompletedItem(self, experience, term, fluency):
        resultList = []

        #if there is experience and the term is not empty, then it must be a skill/role
        if experience and len(term) > 0:
            experience = self.experienceDict[takeClosestNumber(list(self.experienceDict.keys()), experience)]
            resultList.append({
                "skill/role": {"text": term.strip(), "experience": experience}
            })

            experience = None
            term = ""

        #if there is fluency and the term is not empty, then it must be a language
        elif fluency and len(term) > 0:
            fluency = fluency if fluency != "fluent" else "fully-fluent"
            resultList.append({
                "language": {"term": term.strip(), "fluency": fluency}
            })

            fluency = None
            term = ""

        return (experience, term, fluency, resultList)