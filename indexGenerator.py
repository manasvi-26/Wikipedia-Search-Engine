import os
import heapq

class Word:

    def __init__(self, word, text, doc):
        self.word = word
        self.text = text
        self.doc = doc
    
    def __lt__(self,nxt):
        
        if self.word != nxt.word : 
            return self.word < nxt.word
        else : return self.doc < nxt.doc

def Hex(dec):
    return hex(dec).split('x')[-1]

class IndexGenerator:

    def __init__(self):
        self.heap = []    
        self.file_pointers = []

    def writeToFile(self,dict,words,outputFile):

        words = sorted(words)
        file = open(outputFile,"w+")
        labels = ['T','B','I','R','E','C']

        for word in words:
            text = word + ":"
            for pageId in dict[word]:
                text += "D" + Hex(pageId)
                for index in range(6):
                    freq = dict[word][pageId][index]
                    if freq == 0 : continue
                    text += labels[index] + Hex(freq)
            file.write(text)
            file.write('\n')

        file.close()            


    def nextWord(self,fileCnt):

        file = self.file_pointers[fileCnt]
        # print("file is ",file)
        line = file.readline().strip('\n')
        data = line.split(":")
        if data[0] == '': return None
        # print(data[0])
        word = Word(data[0],data[1],fileCnt)

        return word

    def print_word(self,word):
        print(word.word,end="------>")
        print(word.text)

    def merge_files(self,dict,indexFolder,statsFile):

        self.indexFile_pointers = []

        for i in range(36):

            f = open(indexFolder + '/index' + str(i)+ '.txt',"w+")
            self.indexFile_pointers.append(f)


        for file in os.listdir(dict):
            self.file_pointers.append(open(dict + "/" + file))

        for fileCnt in range(len(self.file_pointers)):
            self.heap.append(self.nextWord(fileCnt))


        heapq.heapify(self.heap)

        token_count = 0
        while len(self.heap):

            currWord = self.heap[0]
            text = ""
            token_count += 1

            while len(self.heap) and currWord.word == self.heap[0].word:

                text += self.heap[0].text
                fileCnt = self.heap[0].doc
                heapq.heappop(self.heap)

                newWord = self.nextWord(fileCnt)
                if newWord: 
                    heapq.heappush(self.heap,newWord)

            index = currWord.word[0] 
            
            if currWord.word[0] in "0123456789":
                index = int(currWord.word[0])
            else : index = ord(currWord.word[0]) - 97 + 10
            self.indexFile_pointers[index].write(currWord.word+":"+text+"\n")

        f = open(statsFile,"a")
        f.write(str(token_count)+"\n")