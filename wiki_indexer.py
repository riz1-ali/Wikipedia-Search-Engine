import xml.sax
from nltk.corpus import stopwords
from Stemmer import Stemmer
import re
import sys
import os
from time import time

stop_words = set(stopwords.words('english'))
tot_pages,tot_docs,rem_fill = 0,0,0
thresh = 20000

class Parsing_Class(xml.sax.ContentHandler):
	def __init__(self):
		self.data,self.title,self.text = '',None,None
		self.word_map,self.title_list = {},[]
		self.files,self.pages = 1,0
	def startElement(self,tag,attribute):
		self.data = ''
	def characters(self, content):
		self.data += content
	def fill_f(self,tag):
		global rem_fill
		if len(self.title_list) != thresh and not rem_fill:
			return
		write_f(self.files,self.word_map,self.title_list)
		self.word_map,self.title_list = {},[]
		global tot_pages
		tot_pages += 1
		self.files += tag=="page"
	def endElement(self,tag):
		if tag == 'title' or tag == 'text':
			if tag == 'title':self.title = self.data
			else:self.text = self.data
			self.data = ''
		elif tag == "mediawiki":
			self.fill_f(tag)
		elif tag == 'page':
			if self.pages//thresh == self.files:
				self.fill_f(tag)
			build_index(self.title,self.text,self.pages,self.word_map)
			global tot_docs
			tot_docs = self.pages
			self.pages += 1
			self.title_list.append(self.title)

def write_f(counts,word_map,title_list):
	ft = ['t','b','c','i','r','l']
	c = -1
	with open(path_to_index+'index'+str(counts-1)+'.txt','w') as f:
		for key in sorted(word_map.keys()):
			c += 1
			ans = key + ":"
			for document in word_map[key]:
				ans+='d'+str(document)
				c1 = -1
				for freq in word_map[key][document]:
					c1 += 1
					if freq == 0:
						continue
					ans += str(ft[c1])+str(freq)
			f.write(ans+'\n')
		f.close()
	with open('./titles/title'+str(counts-1)+'.txt','w') as f:
		for t in title_list:f.write(t+'\n')
		f.close()

stemmer = Stemmer('porter')

def tokenize(text):
	res = []
	for token in re.split(r'[^A-Za-z0-9]+',text):
		word = stemmer.stemWord(token.lower())
		if len(word) >= 2 and word not in stop_words:
			res.append(word)
	return res

def increment_index(index,pages,word_map,tokens):
	for token in tokens:
		prevs = [0]*6
		if token not in word_map.keys():
			word_map[token] = {}
			prevs[index] += 1
			word_map[token][pages] = prevs
		else:
			if pages in word_map[token]:
				word_map[token][pages][index] += 1
			else:
				prevs[index] += 1
				word_map[token][pages] = prevs

def extract_category(content):
	res = []
	for text in re.findall(r"\[\[Category:(.*)\]\]", str(content)):
		res.extend(tokenize(text))
	return res

def extract_infobox(content):
	res = []
	if '{{Infobox' not in content: return res
	for block in content.split('{{Infobox'):
		for line in block.split('\n'):
			if line == '}}': break
			res.extend(tokenize(line))
	return res

def extract_references(content):
	res = []
	if '==References==' not in content: return res
	delim = ['==','[[Category','DEFAULTSORT']
	rem = ['reflist','Reflist']
	for line in (content.split('==References==')[1]).split('\n'):
		f = False
		for i in delim: f |= i in line
		if f: break
		line = tokenize(line)
		for i in rem:
			if i in line:
				line.remove(i)
		res.extend(line)
	return res

def extract_links(content):
	res = []
	if '==External links==' not in content: return res
	for line in (content.split('==External links==')[1]).split('\n'):
		if line == '': continue
		if line[0] == '*':res.extend(tokenize(line))
	return res

def build_index(title,text,pages,word_map):
	func_ptr = [tokenize,tokenize,extract_category,
				extract_infobox,extract_references,extract_links]
	body = title
	for i in range(len(func_ptr)):
		increment_index(i,pages,word_map,func_ptr[i](body))
		body = text

def merge(id1,id2):
	if id1 != id2:
		f1 = open(path_to_index+'index'+str(id1)+'.txt','r')
		f2 = open(path_to_index+'index'+str(id2)+'.txt','r')
		f3 = open('./temp.txt','w')
		w1,w2 = f1.readline(),f2.readline()
		w1,w2 = w1.strip('\n'),w2.strip('\n')
		while w1 and w2:
			word_1,word_2 = w1.split(':')[0],w2.split(':')[0]
			if word_1 != word_2 :
				if min(word_1,word_2) == word_1:
					f3.write(w1+'\n')
					w1 = f1.readline()
					w1 = w1.strip('\n')
				else:
					f3.write(w2+'\n')
					w2 = f2.readline()
					w2 = w2.strip('\n')
			else:
				s = word_1 + ':'
				s += w1.split(':')[-1]
				s += w2.split(':')[-1]
				f3.write(s+'\n')
				w1,w2 = f1.readline(),f2.readline()
				w1,w2 = w1.strip('\n'),w2.strip('\n')
		while w1:
			f3.write(w1+'\n')
			w1 = f1.readline()
			w1 = w1.strip('\n')
		while w2:
			f3.write(w2+'\n')
			w2 = f2.readline()
			w2 = w2.strip('\n')
		f1.close()
		f2.close()
		f3.close()
		os.remove(path_to_index+'index'+str(id1)+'.txt')
		os.remove(path_to_index+'index'+str(id2)+'.txt')
		os.rename('./temp.txt',path_to_index+'index'+str(id1//2)+'.txt')

def merge_index():
	global tot_pages
	merge_con = tot_pages
	while merge_con > 1:
		for i in range(0,merge_con,2):
			if i+1 == merge_con:
				os.rename(path_to_index+'index'+str(i)+'.txt',path_to_index+'index'+str(i//2)+'.txt')
				break
			merge(i,i+1)
		merge_con = merge_con//2 + merge_con%2

def split_index():
	files,tokens = 0,0
	os.rename(path_to_index+'index0.txt',path_to_index+'all.txt')
	f1,f2 = open(path_to_index+'all.txt','r'),open(path_to_index+'sec_index.txt','w')
	buf = []
	for line in f1:
		buf += [line.strip('\n')]
		if len(buf)//thresh:
			f2.write(buf[0].split(':')[0]+'\n')
			f = open(path_to_index+'index'+str(files)+'.txt','w')
			for i in buf: f.write(i+'\n')
			f.close()
			files += 1
			tokens += thresh
			buf = []
	f1.close()
	if len(buf):
		f2.write(buf[0].split(':')[0]+'\n')
		f = open(path_to_index+'index'+str(files)+'.txt','w')
		for i in buf: f.write(i+'\n')
		f.close()
		files += 1
		tokens += len(buf)
		buf = []
	f2.close()
	os.remove(path_to_index+'all.txt')
	return files,tokens

path_to_dump = [sys.argv[1]]

path_to_index = './index/'
if not os.path.exists(path_to_index):
	os.mkdir(path_to_index)
if not os.path.exists('./titles'):    
	os.mkdir('./titles/')
path_to_save_stats = './stats.txt'

tot_pages,tot_docs,rem_fill = 0,0,0

parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces,0)
parser.setContentHandler(Parsing_Class())
start_t = time()
for i in range(len(path_to_dump)):
	if i == len(path_to_dump)-1:
		rem_fill = 1
	parser.parse(path_to_dump[i])
print("Index Creation Time:",time()-start_t)

start_t = time()
merge_index()
print("Index Merging Time:",time()-start_t)

start_t = time()
res = split_index()
print("Index Splitting Time:",time()-start_t)

with open(path_to_save_stats,'w') as file:
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(path_to_index):
		for f in filenames:
			fp = os.path.join(dirpath, f)
			if os.path.islink(fp): continue
			total_size += os.path.getsize(fp)
	total_size /= 1024 #KB
	total_size /= 1024 #MB
	total_size /= 1024 #GB
	file.write(str(total_size)+'GB\n')
	file.write(str(res[0])+'\n')
	file.write(str(res[1])+'\n')
	file.close()

with open('./doc_count.txt','w') as f:
	f.write(str(tot_docs)+','+str(thresh)+'\n')
	f.close()
