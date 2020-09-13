import sys
from nltk.corpus import stopwords
from Stemmer import Stemmer
import re
from time import time
from collections import defaultdict
from bisect import bisect_right
from math import log2
from linecache import getline

stemmer = Stemmer('porter')
stop_words = set(stopwords.words('english'))

def tokenize(text):
	res = []
	for token in re.split(r'[^A-Za-z0-9]+',text):
		word = stemmer.stemWord(token.lower())
		if len(word) >= 2 and word not in stop_words:
			res.append(word)
	return res

secondary = []
with open('./index/sec_index.txt','r') as f:
	for i in f.readlines():
		line = i.strip('\n')
		secondary += [line]
	f.close()

title_nums,thresh = 0,0

with open('./doc_count.txt','r') as f:
	for i in f.readlines():
		title_nums,thresh = [int(x) for x in i.strip('\n').split(',')]
		title_nums += 1
		break
	f.close()

def get_post_list(word):
	idx = bisect_right(secondary,word)-1
	if idx >= 0:
		f = open('./index/index'+str(idx)+'.txt','r')
		for i in f:
			line = i.strip('\n').split(':')
			if line[0] == word:
				return line[1]
	return None

ft = ['t','b','c','i','r','l']
rel_w = [0.5,0.5,0.25,0.125,0.0625,0.0625]
term_freq = defaultdict(lambda : [0] * 8)

def get_count(strx, chars):
	ans = 0
	if chars in strx:
		part = strx.split(chars)[1]
		ans = int(re.split(r'[^0-9]+', part)[0])
	return ans

def evaluate(posting_list,idxs):
	posting_list = 'd'+posting_list
	flag = 0
	doc_c = get_count(posting_list,'d')
	for i in idxs:
		if ft[i] not in posting_list:
			continue
		flag = 1
		term_freq[doc_c][i+1] += 1
		term_freq[doc_c][7] += get_count(posting_list,ft[i])*log2(title_nums/posting_list.count(ft[i]))


start_time,tot_q = time(),0
f = open(sys.argv[1],'r')
res_f = open('./queries_op.txt','w')
for i in f:
	tot_q += 1
	line = i.strip('\n').split(',')
	num_results,query = int(line[0]),line[1]
	qt_idx = []
	for j in range(len(ft)):
		if ft[j]+':' in query:
			qt_idx.append(j)
	term_freq = defaultdict(lambda : [0] * 8)
	if qt_idx==[]:
		qt_idx.extend([0,1])
		for token in tokenize(query):
			posting_list = get_post_list(token)
			if posting_list != None :
				for doc in posting_list.split('d')[1:]:
					evaluate(doc,qt_idx)
	else:
		for j in qt_idx:
			exp = re.escape(ft[j]+':') + "(.*)"
			keys = []
			for term in re.findall(exp, str(query))[0].split(" "):
				if ':' in term:
					break
				keys.extend(tokenize(term))
			for token in keys:
				posting_list = get_post_list(token)
				if posting_list != None :
					for doc in posting_list.split('d')[1:]:
						evaluate(doc,[j])
	for res in sorted(term_freq.items(), key=lambda x: x[1], reverse = True)[:num_results]:
		title = getline('./titles/title'+str(res[0]//thresh)+'.txt',res[0]%thresh+1)
		res_f.write(str(res[0])+', '+title)

res_f.write(str(time()-start_time)+','+str((time()-start_time)/tot_q)+'\n')
