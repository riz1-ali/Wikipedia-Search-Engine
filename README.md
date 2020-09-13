# Wikipedia Search Engine

### To build the indexes, run 
```
user@linux:~/Wikipedia-Search-Engine$ python3 wiki_indexer.py <path to wikipedia dump>
```
##### A separate file ```doc_count.txt``` was kept. It has the number of documents in the dump (zero-based) and the threshold used for splitting, separated by comma.
##### ```stats.txt``` stores the total size of index, along with the number of index files built and total number of tokens in the dump, all in separate lines.
##### The search file ```search.py``` requires ```doc_count.txt``` for the threshold and number of documents.

### To search/query, run
```
user@linux:~/Wikipedia-Search-Engine$ python3 search.py <path to file containing queries>
```
##### The queries file should have in a single line, a number K, and the query. Top K results would be displayed relevant to the query

### Sample Query File:-
```
100, t:World Cup i:2019 c:Cricket
25, t:the two towers i:1954
```
##### To search in some specific fields, use the following:- t: for Title, b: for Body, c: for Category, i: for Infobox, r: for References, l: for Links. Type the query in the field after mentioning this. You can refer the above queries for further information on the syntax.
