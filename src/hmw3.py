########################################################################################################################
###### EXTRACTOR #######################################################################################################
########################################################################################################################

import time
import xml.etree.cElementTree as ET
import spacy # spaCy is a library for advanced natural language processing in Python and Cython. https://spacy.io/docs/usage/
import glob
import gzip
import pickle


###### LOAD RESOURCES ##################################################################################################

print('loading model...') # english nlp spacy model used for pos tagging and syntactic dependency parsing
nlp = spacy.load('en')
print('model loaded')

files = [] # list with the path of the folders containing the xml files
for folder in range(180, 360):  # specify folders that must be analyzed
    files.extend(glob.glob("D:/Universita/Intelligenza_Artificiale_e_Robotica/Natural_language_processing/babelfied-wikipediaXML/" + str(folder) + "/*.gz"))


def parse_xmlgz(path):  # given the path of a gzipped xml file, return the easy-accessible structured tree of the file
    with gzip.open(path) as f:
        return ET.fromstring(f.read())

###### EXTRACTION ######################################################################################################

eta = 2  # minimum occurrences of a relation allowed
treshold_len_pi = 1  # minimum length of a relation allowed

I = []  # list of triples with source sentence and babelnet tags (h1, pi, h2, sentence, bn_tag_h1, bn_tag_h2)
P = []  # list of relations
count_pi = {}  # dictionary. key: relation. value: number of occurrences of the relation
counter_IP = -1  # index of relation pi in I
dic_of_I_by_pi = {}  # dictionary: key: relation. value: index of the triples in the list I containing the relation

start_time = time.time()  # working info: time, relations founded
counter_files = 0

for file in files:
    counter_files += 1
    if counter_files % 100 == 0:  # print a status on the console every 100 files
        try:
            print(counter_files, 'of', len(files), '\t\trelations :', len(count_pi), '\t\ttime :', time.time() - start_time)
        except NameError:
            pass
    try:  # There are reading problems in few files
        root = parse_xmlgz(file)
        text = root[0].text
        sentences = text.split('\n')
        words = text.split()

        sentence_anchor = -1  # index of the sentence
        anchor = -1  # index of the word (number of interruption (spaces) before the word)
        anchorStart_sentence = 0  # anchor value at the beginning of a sentence
        annotation_index = 0
        num_annotations = len(root[-1])  # number of annotations in the xml file

        for sentence in sentences:
            original_sentence = sentence  # current sentence
            sentence = sentence.split()  # to list of words
            anchor += 1
            sentence_anchor += 1
            for word in sentence:
                anchor += 1
                if word == '.':  # if it is the end of a sentence
                    hyperlink_indexes = []  # list of tuples containing hyperlink start anchor, end anchor, babelnet code (anch_start, anch_end, bn_tag)
                    anchorEnd_sentence = anchor  # anchor value at the end of a sentence
                    for i in range(annotation_index, num_annotations):  #  iterating on all the annotations related to the sentence
                        if int(root[-1][i][-2].text) > anchorEnd_sentence:  # if the annotation is related to the next sentence
                            annotation_index = i
                            break
                        if root[-1][i][-1].text == 'HL':  # if the annotation corresponds to an hyperlink
                            hyperlink_indexes.append((int(root[-1][i][-3].text), int(root[-1][i][-2].text), root[-1][i][-5].text)) # save the tuple

                    num_hyperlink_indexes = len(hyperlink_indexes)
                    if num_hyperlink_indexes > 1:  # if the sentence has more than one hyperlink
                        H_sent = []  # couples of all hyperlinks in the sentence
                        for i in range(num_hyperlink_indexes):
                            for j in range(i + 1, num_hyperlink_indexes):
                                if hyperlink_indexes[j][0] - hyperlink_indexes[i][1] >= treshold_len_pi:
                                    H_sent.append((hyperlink_indexes[i], hyperlink_indexes[j]))
                        for couple in H_sent:  # iterating on all the couples of hyperlinks
                            # building the subsentence composed by h1, pi, h2
                            h1 = ' '.join([words[i] for i in range(couple[0][0] - sentence_anchor, couple[0][1] - sentence_anchor)])
                            h2 = ' '.join([words[i] for i in range(couple[1][0] - sentence_anchor, couple[1][1] - sentence_anchor)])
                            pi = ' '.join([words[i] for i in range(couple[0][1] - sentence_anchor, couple[1][0] - sentence_anchor)])

                            result = nlp(u'X ' + pi + ' Y')  # analysis of the sentence "X pi Y"
                            dep_xy = [result[0].dep_[1:5], result[-1].dep_[1:4]]  # dependency tag for X and Y

                            # if X is a subject and Y an object, if there is a VERB in pi, if Y has among his ancestors the parent of X (the VERB)
                            if dep_xy[0] == 'subj' and dep_xy[1] == 'obj':
                                if result[0].head.is_ancestor_of(result[-1]) and result[0].head.pos_ == 'VERB':
                                    I.append((h1, pi, h2, original_sentence, couple[0][2], couple[1][2]))
                                    P.append(pi)
                                    counter_IP += 1
                                    try:
                                        dic_of_I_by_pi[pi].append(counter_IP)
                                    except KeyError:
                                        dic_of_I_by_pi[pi] = [counter_IP]
                                    try:
                                        count_pi[pi] += 1
                                    except KeyError:
                                        count_pi[pi] = 1
                                    break
    except (AttributeError, ET.ParseError):
        print('Error at:', counter_files, 'file: skip')  # show the error file
        pass
    # if counter_files == 100:
    #     break

pickle.dump(dic_of_I_by_pi, open("dic_of_I_by_pi_180-360.p", "wb"))  # save a dic of triples by relation
pickle.dump(I, open("FULLtriples_folder_180-360.p", "wb"))   # save all relations, even the ones with occurrences < eta

##### DISCARD RELATIONS WITH OCCURRENCES < ETA #########################################################################

to_delete_I_indexes = []  # index of the triples that has to be deleted
for i in reversed(range(len(P))):  # iterating on all founded realtions
    if count_pi[P[i]] < eta:  # if the relation occurrences are less than eta
        to_delete_I_indexes.extend(dic_of_I_by_pi[P[i]])   # save the index of the triple
        P.pop(i)  # remove the relation
to_delete_I_indexes.sort()  # decrescent order of the indexes
to_delete_I_indexes.reverse()
for i in to_delete_I_indexes:  #delete triples
    I.pop(i)

pickle.dump(I, open("triples_folder_180-360.p", "wb"))  # save filtered relations

# for i in range(len(P)):
#     print(I[i])
#     print(P[i])
#     print('\n')