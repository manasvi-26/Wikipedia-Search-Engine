# Wikipedia Search Engine

## **Index Creation**

The index has ~20 million tokens, split into 36 files based on first character of each token. The tokens are sorted alphabetically in these files. The index can be found in `index` folder - created with `indexer.py` and `indexGenerator.py`.

Titles are stored in 428 files in `titles` folder.

### **Method**

- Write to the disk (sorted manner) after every 10,000 documents
- Once inverted index is created in separate files, merge them
- Merging done by maintaing a heap structure and writing to another set of index files
- Store title of each document
- The Posting list for each token is in the following format:

    `Word:D[doc Id in hex]T[ title freq in hex]B[body freq in hex]C[body freq in hex]I[info freq in hex]R[ref freq in hex]E[links freq in hex]`

## **Search**

Search utilizes the titles folder and index folder mentioned above.

### **Method**

- Lowercase, tokenize, and stem the query
- Search for the index file that has the query term's posting list by looking at the first character in the word.
- Binary Search in that corresponding index file for the word
- *Calculate* the tf-idf score based on different weights allotted for t,b,i,r,l,c
- Sort the documents and display the 10-best documents