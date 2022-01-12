import re
import Stemmer
import sys
import json
import math
import time

total_docs = 21384756

class Searcher:

    def __init__(self,file):
        self.stemmer = Stemmer.Stemmer('english')
        
        self.indexFile_pointers = []
        for i in range(36):
            f = open("./index/index" + str(i) + ".txt","r")
            self.indexFile_pointers.append(f)
        
        
        self.outputFile = open(file,"w+")



    def parseQuery(self,query):
        
        pattern = "[tibcre]:"
        data = {}

        if not re.search(pattern,query) : data["a"]  = query
        else:
            for match in re.finditer(pattern, query):
                key = query[match.start()]

                start = match.end()
                end = re.search(pattern,query[start:]) 
                
                if not end : end = len(query)
                else : end = end.start() + start
                data[key] = query[start : end]


        docs = {}

        for key,value in data.items():
            words = re.split("[^A-Za-z0-9]+",value)
            for word in words:
                if word == '': continue
                word = word.lower()
                word = self.stemmer.stemWord(word) 
                
                # print(word)
                posting_list = self.binarySearch(word)
                all_docs = posting_list.split("D")
                
                
                for doc in all_docs :
                    if doc == "" : continue
                    score,docId = self.calculate_tfIdfScore(key,"D"+doc)
                    try:
                        docs[docId] += score
                    except:
                        docs[docId] = score

        #get all doc Ids in decreasing order of tfidf
        docs_list = list(docs.items())
        docs_list.sort(key=lambda x: x[1], reverse = True)
        k = min(len(docs_list),10)
        docIds = list(docs_list[:k])

        docIds = [tup[0] for tup in docIds]
        # print(docIds)
        return docIds



    def get_freqInDoc(self,doc):
        
        frequency = {}

        pattern = "[DBICETR]"

        for match in re.finditer(pattern, doc):
            key = doc[match.start()].lower()

            start = match.end()
            end = re.search(pattern,doc[start:]) 

            if not end : end = len(doc)
            else : end = end.start() + start
            
            frequency[key] = int(doc[start : end],16)


        return frequency


    def calculate_tfIdfScore(self,field_type,doc):

        weights = {"t" : 300 , "b" : 1, "c": 50, "i": 75, "e" : 0.5,"r" : 0.5, "d" : 0}

        frq = self.get_freqInDoc(doc)     
        docId = frq["d"]
        
        curr_sum = 0
        for key, value in frq.items():
            curr_sum += weights[key]*value
        
        if field_type != "a" : 

            try: curr_sum += 5000 * frq[field_type]
            except: curr_sum += 0

        tf = math.log(1 + curr_sum,10)
        idf = math.log(total_docs/len(doc), 10)

        score = tf * idf

        return score,docId



    def binarySearch(self, word):
        start = time.time()

        if word[0] in "0123456789":
            index = int(word[0])
        else : index = ord(word[0]) - 97 + 10

        f = self.indexFile_pointers[index]
        f.seek(0,2)  # Seek to EOF.
        size = f.tell()

        low , high = 0, size - 1

        while low < high :
            mid = (low + high) >> 1

            # Just to figure out where our line starts.
            f.seek(max(mid -1,0)) 

            # Ignore previous line, find our line.
            f.readline()  

            line = f.readline().strip("\n")
            data = line.split(":")
            
            if(data[0] == word ) : 
                return data[1]
            if(data[0] < word) : low = mid + 1
            if(data[0] > word) : high = mid - 1

        return ""

    def get_titles(self,docIds):

        for doc in docIds :

            titleFile = doc//50000 + 1
            lineNumber = doc%50000 - 1
            # print(titleFile)

            f = open("./titles/titles" + str(titleFile) + ".txt")
            lines = f.readlines()

            self.outputFile.write(lines[lineNumber])



if __name__ == "__main__":

    queryFile = sys.argv[1]
    file = open(queryFile,"r")

    outputFile = sys.argv[2]

    searcher = Searcher(outputFile)

    # read the qeuery file
    cnt = 1
    while True:

        start = time.time()
        
        query = file.readline()
        if not query:break
        
        docIds = searcher.parseQuery(query)
        if len(docIds) == 0:
           searcher.outputFile.write("no related documents found\n") 
        searcher.get_titles(docIds)
        
        end = time.time()
        searcher.outputFile.write("Search Time: " + str(end - start) + "\n\n")
        # text = "Query " + str(cnt) + " Done"
        # cnt+= 1
        # print(text)