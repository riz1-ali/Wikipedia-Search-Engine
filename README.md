### Information Retrieval and Extraction: Mini Project (Phase 2)
#### Name: Rizwan Ali
#### Roll Number: 20171167

- **Space Available on ADA is approx 25 GB (approx 27 GB with exceeding space limit)**. While Merging Indexes, an approach similar to the Merge Function in Merge Sort was Used. Roughly, the size of index is around 14 GB (13.3 GB to be precise). The last step in merging requires 13.3*2 GB times the space. While building the index, the program crashes mid way merging files, due to exceeding memory limit. Hence, Merging and Splitting were done separately on the complete dump. Although the complete program was tested on 3-4 dumps topgether, it worked perfectly.
- The stats report in stats.txt were calculated after splitting the indexes, including the size and number of tokens in the index. This was done using a Python code.
- A separate file ```doc_count.txt``` was kept. It has the number of documents in the dump (zero-based) and the threshold used for splitting, separated by comma.
- Currently, you have to add the paths to the wikidumps in the code manually in a list ```path_to_dump```. This was done because there was no explanation of how to provide the paths to the dumps. Furthermore, the index creation was done on **ADA**, hence the paths were hardcoded (dumps were in ```/scratch```).
- The search file ```search.py``` requires ```doc_count.txt``` for the threshold and number of documents.
- A secondary index was kept in a file ```sec_index.txt``` which has the first word of every index file created. Since the indexes are sorted, **binary searching** over the terms in ```sec_index.txt``` could help us finding which index file would have the query word, if present.
- The threshold for number of tokens in an index file is $$20000$$.
- Titles were also stored in a distributed fashion, i.e., all the titles were split across multiple files, with each file having at most $$20000$$ titles only.
- Titles are stored in a directory named ```titles```. Similarly, indexes are stored in a directory named ```index```.
