########################################################################################################################
###### CODE FOR THE GENERATION OF THE PROVIDED CHARTS ##################################################################
########################################################################################################################

# README: the requested pickle file can be generated with hmw3.py or downloaded at (100 MB total):
# https://www.dropbox.com/s/pljitomr1xve5z4/dic_of_I_by_pi_0-180.p?dl=0
# https://www.dropbox.com/s/alntsnlk0y4rgky/dic_of_I_by_pi_180-360.p?dl=0

# now are activated the lines for the second chart

import spacy
import pickle

# print('loading model...')
# nlp = spacy.load('en')
# print('model loaded\n')

#I = pickle.load(open("triples_folder_0-180.p", "rb"))
# I = pickle.load(open("triples_folder_180-360.p", "rb"))
# I_full = pickle.load(open("FULLtriples_folder_0-180.p", "rb"))
# I_full1 = pickle.load(open("FULLtriples_folder_180-360.p", "rb"))
dic_of_I_by_pi = pickle.load(open("dic_of_I_by_pi_0-180.p", "rb"))
dic_of_I_by_pi1 = pickle.load(open("dic_of_I_by_pi_180-360.p", "rb"))

# d = {}
# for k in dic_of_I_by_pi:
#     d[k] = dic_of_I_by_pi[k] + dic_of_I_by_pi1[k]
dic_of_I_by_pi.update(dic_of_I_by_pi1)

to_remove_keys = []
for k in dic_of_I_by_pi:
    if k[0] in [',', ')', "'", ':'] or 'and' in k or k == 's' or k[0:2] == 's ':
        to_remove_keys.append(k)

for item in to_remove_keys:
    dic_of_I_by_pi.pop(item)


pi_occurrences = [0] * 2800
pi_examples = [''] * 2800
for k in dic_of_I_by_pi:
    pi_occurrences[len(dic_of_I_by_pi[k])] += 1
    if len(k) > 30:
        pi_examples[len(dic_of_I_by_pi[k])] = k[0:30] + '...'
    else:
        pi_examples[len(dic_of_I_by_pi[k])] = k
for i in range(2800):
    if pi_occurrences[i] != 0:
        print(i, '\t', pi_occurrences[i], '\t', pi_examples[i])




# length_pi_I = [0] * 100
# for item in I_full:
#     try:
#         length_pi_I[len(item[1].split())] += 1
#     except:
#         pass
# for item in I_full1:
#     try:
#         length_pi_I[len(item[1].split())] += 1
#     except:
#         pass

# for i in range(100):
#     print(i, '\t', length_pi_I[i])
