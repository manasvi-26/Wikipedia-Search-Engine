import xml.sax
import time
import re
import Stemmer
from nltk.corpus import stopwords 
import indexGenerator
import os
import sys

class Indexer(xml.sax.ContentHandler):

    def __init__(self):

        self.titleFile = open("title.txt","w+")

        self.title = []
        self.body = [] 
        self.current_tag = ""
        self.generate_parser()
        
        self.currWords = set()
        
        self.dict = {}
        self.stemmer_dict = {}

        self.pageId = 0
        self.indexCnt = 0

        self.indexGenerator = indexGenerator.IndexGenerator()
        self.stemmer = Stemmer.Stemmer('english')
        self.stopWords = set(stopwords.words('english'))
        arr = ['cite','reflist','refbegin','jpg', 'png', 'jpeg','ref','refend']
        for i in arr: self.stopWords.add(i)        

        self.total_tokens = set()

    def generate_parser(self):

        self.parser = xml.sax.make_parser()
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.parser.setContentHandler(self)

    def startElement(self,tag,attributes):
        self.current_tag = tag
        self.generate_parser()

    def endElement(self,tag):
        if(tag == "page"):
            self.pageId += 1
            print("\r", self.pageId,en, flush=Trued="")
            
            
            self.tokenize()

            if self.pageId % 10000 == 0:
                
                self.indexGenerator.writeToFile(self.dict,self.currWords,"./outputs/index"+str(self.indexCnt)+".txt")
                self.dict = {}
                self.currWords = set()
                self.indexCnt += 1

            self.title = []
            self.body = []
            
        if tag == "mediawiki":
            self.indexGenerator.writeToFile(self.dict,self.currWords,"./outputs/index"+str(self.indexCnt)+".txt")


    def characters(self,content):
        if(self.current_tag == "title"):
            self.title.append(content)
        if(self.current_tag == "text"):
            self.body.append(content)

    
    def parseFile(self, path):
        self.parser.parse(path)


    def clean_data(self,data):

        pattern = "https?://\S+|[^A-Za-z0-9]+"
        tokens = []
        for str in data :
            words = re.split(pattern,str)
            for word in words:
                if word == "": continue
                self.total_tokens.add(word)

                if word in self.stemmer_dict: stemmedWord = self.stemmer_dict[word]
                else : 
                    stemmedWord = self.stemmer.stemWord(word) 
                    self.stemmer_dict[word] =stemmedWord

                if len(stemmedWord) > 16: continue
                if len(stemmedWord) > 4 and stemmedWord[0] in '0123456789': continue
                
                
                if stemmedWord not in self.stopWords:
                    tokens.append(stemmedWord)
        
        return tokens

    def parseInfoBox(self):
        
        data = []
        indices = [[0,0]]

        pattern = '{{infobox'
        for match in re.finditer(pattern, self.body):
            
            s = match.start()
            e = match.end()


            #we do stack kinda approach to find end bracket sequence of InfoBox
            iter = e
            cnt = 2

            while cnt != 0:
                try:
                    if self.body[iter] == '{': cnt += 1
                    if self.body[iter] == '}': cnt -= 1
                    iter += 1
                except :
                    text = self.body[e : iter]
                    data.append(text)

                    return self.clean_data(data),indices

            indices.append([s,iter])

            text = self.body[e : iter]
            data.append(text)

        data = self.clean_data(data)
        return data,indices

    def parseCategories(self):

        pattern = '\[\[category:(.*?)\]\]'
        data = []


        for match in re.finditer(pattern,self.body):
            s = match.start()
            e = match.end()
            
            str = re.split('\[\[category:|]]',self.body[s:e])[1]
            data.append(str)

        data = self.clean_data(data)
        return data

    def parseReferences(self):

        pattern = '==references=='
        end_pattern = '==[a-z]+==|\[\[category:(.*?)\]\]'
        
        match = re.search(pattern, self.body)
        if not match : return []

        s = match.end()

        end = re.search(end_pattern,self.body[s:])
        if end : e = s + end.start()
        else : e = -1

        data = [self.body[s:e]]     

        data = self.clean_data(data)
        return data


    def parseLinks(self):

        pattern = '==external link(s*)=='
        end_pattern = '==[a-z]+==|\[\[category:(.*?)\]\]'

        data = []

        for match in re.finditer(pattern,self.body):
          
            s = match.end()
            end = re.search(end_pattern,self.body[s:])
            if end : e = s + end.start()
            else : e = -1

            data.append(self.body[s:e])

        data = self.clean_data(data)
        return data

    def parseBody(self, InfoIndices):
        
        data = []
        s = 0
        for ind in InfoIndices:
            data.append(self.body[s:ind[0]])
            s = ind[1]

        end_pattern = '==external link(s*)==|\[\[category:(.*?)\]\]|==references==|==notes==|==bibliography=='
        end = re.search(end_pattern,self.body[s:])
        if end : e = s + end.start()
        else: e = -1

        data.append(self.body[s:e])
        data = self.clean_data(data)
        return data
    

    def addWordToDict(self,word,type):

        if word in self.dict and self.pageId not in self.dict[word]:
            self.dict[word][self.pageId] = [0,0,0,0,0,0]
        elif word not in self.dict :
            self.dict[word] = {self.pageId : [0,0,0,0,0,0]}

        self.dict[word][self.pageId][type] += 1

        self.currWords.add(word)

    def tokenize(self):
        
        self.title = "".join(self.title)
        self.body = "".join(self.body)

        self.titleFile.write(self.title)

        self.title = self.title.lower()
        self.body = self.body.lower()

        #parse title 
        titleData = self.clean_data([self.title])
        for word in titleData : self.addWordToDict(word,0)


        #parse infoBox
        infoBoxData , infoBoxIndices = self.parseInfoBox()
        for word in infoBoxData : self.addWordToDict(word,2)
        

        #parse categories
        categoriesData = self.parseCategories()
        for word in categoriesData : self.addWordToDict(word,5)
       
        #parse references
        referencesData = self.parseReferences()
        for word in referencesData : self.addWordToDict(word,3)
      
        #parse external links
        linksData = self.parseLinks()
        for word in linksData : self.addWordToDict(word,4)
       
        #parse body
        bodyData = self.parseBody(infoBoxIndices)   
        for word in bodyData : self.addWordToDict(word,1)



if __name__ == '__main__':

    try:
        os.mkdir('outputs')
    except FileExistsError:
        print("Dir exists already", flush=True)
    
    wikiDump = sys.argv[1]

    pathToIndexFolder = "indexFolder"
    # f = open(pathToIndexFolder+"/index.txt","w+")

     
    try:
        os.mkdir(pathToIndexFolder)
    except FileExistsError:
        print("Dir exists already", flush=True)
    

    indexer = Indexer()
    indexer.parseFile(wikiDump)

    statsFile = sys.argv[2]
    f = open(statsFile,"w+")
    f.write(str(len(indexer.total_tokens))+"\n")
    f.close()

    indexer.indexGenerator.merge_files('outputs', pathToIndexFolder,statsFile)
    