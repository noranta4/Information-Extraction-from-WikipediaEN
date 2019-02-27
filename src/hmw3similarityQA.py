########################################################################################################################
###### TRIPLE MAPPING ##################################################################################################
########################################################################################################################

import spacy  # spaCy is a library for advanced natural language processing in Python and Cython. https://spacy.io/docs/usage/
import pickle

print('loading model...')  # english nlp spacy model used for syntactic dependency parsing
nlp = spacy.load('en')
print('model loaded\n')


###### LOAD QUESTION RESOURCES AND QA GENERATOR ########################################################################

part = []  # lists containing designed questions for the different classes
material = []
generalization = []
specialization = []
time = []
with open('patterns.tsv') as f:  # filling the lists
    for line in f:
        try:
            q = line.split('\t')
            if q[1] == 'part\n':
                part.append(q[0])
            elif q[1] == 'material\n':
                material.append(q[0])
            elif q[1] == 'generalization\n':
                generalization.append(q[0])
            elif q[1] == 'specialization\n':
                specialization.append(q[0])
            elif q[1] == 'time\n':
                time.append(q[0])
        except:
            pass


def generate_qa(quest, subj, obj, answer):
    final_question = ''
    x_flag = 0
    y_flag = 0
    for c in quest:
        if c == 'X':
            final_question += subj
            x_flag = 1
        elif c == 'Y':
            final_question += obj
            y_flag = 1
        else:
            final_question += c
    if x_flag == 1 and y_flag == 1:  # management of binary questions and open questions
        return final_question + '\t' + answer
    elif x_flag == 0 and y_flag == 1 and answer == 'yes':
        return final_question + '\t' + subj
    elif x_flag == 1 and y_flag == 0 and answer == 'yes':
        return final_question + '\t' + obj
    else:
        return 0  # return exception


###### SIMILARITY KERNEL ###############################################################################################

r1 = 'is part of the'  # pi seed
questions = list(part)  # list of questions of the chosen class
relation = 'part'  # class
simil_threshold = 0.87  # similarity barrier threshold on the seed
print('seed :\t', r1)
path = "triples_folder_0-180.p"
path1 = "triples_folder_180-360.p"
I = pickle.load(open(path, "rb")) + pickle.load(open(path1, "rb"))  # list of triples


def sim(pi1, pi2):
    doc1 = nlp(u'X ' + pi1 + ' Y')  # analysis of the sentences "X pi Y"
    doc2 = nlp(u'X ' + pi2 + ' Y')

    shortest_path_1 = list(doc1[-1].ancestors)  # extraction of the shortest paths, list of the words
    shortest_path_2 = list(doc2[-1].ancestors)

    dep_pi_sp1 = [doc1[0].dep_] + [w.dep_ for w in shortest_path_1] + [doc1[-1].dep_]  # shortest paths, list of the dep tags
    dep_pi_sp2 = [doc2[0].dep_] + [w.dep_ for w in shortest_path_2] + [doc2[-1].dep_]

    if dep_pi_sp1 != dep_pi_sp2:  # if different dep tags
        return 0
    elif str(doc2[1]) in [',', ')', "'", "''", ':'] or 'and' in pi2:  # additional filter
        return 0
    else:
        similarity = 0
        num_words = len(shortest_path_1)
        for i in range(num_words):
            similarity += shortest_path_1[i].similarity(shortest_path_2[i])  # word2vec similarity between words in the shortest path
        # the verb count as the whole sentence (or the attribute if the verb is be or have)
        if shortest_path_1[-1].lemma_ in ['have', 'be'] and shortest_path_2[-1].lemma_ in ['have', 'be']:
            similarity += num_words * shortest_path_1[-2].similarity(shortest_path_2[-2])
        else:
            similarity += num_words * shortest_path_1[-1].similarity(shortest_path_2[-1])
        similarity /= (2 * num_words)  # normalization

        return round(similarity, 3)


###### TRIPLE MAPPING ##################################################################################################

print('similarity threshold', simil_threshold, '\n')
extracted_couples = []  # list of all extracted couples (h1, h2)
full_extracted_pentaples = []  # list of all extracted pentaples (h1, h2, example_sentence, BN1, BN2)
for item in I:  # keep the triples similar to the seed
    simil = sim(r1, item[1])
    if simil >= simil_threshold:
        if (item[0], item[2]) not in extracted_couples:
            extracted_couples.append((item[0], item[2]))
            full_extracted_pentaples.append((item[0], item[2], item[3], item[4], item[5]))
            # print(item[0] + '\t' + 'part' + '\t' + item[2])  # activate for the generation of triples.tsv


###### QA GENERATION ###################################################################################################

f = open('question-answer-pairs.txt', 'a', encoding='utf-8')
already_questioned = []
for pentaple in full_extracted_pentaples:
    for question in questions:  # all positive questions from the pentaple
        f.write(str(generate_qa(question, pentaple[0], pentaple[1], 'yes')) + '\t' + relation + '\t"' + pentaple[2] + '"\t' + pentaple[3] + '\t' + pentaple[4] + '\n')
    already_questioned.append((pentaple[0], pentaple[1]))
    for pentaple1 in full_extracted_pentaples:  # all the negative questions from the pentaple
        if (pentaple[0], pentaple1[1]) not in already_questioned:
            already_questioned.append((pentaple[0], pentaple1[1]))
            if (pentaple[0], pentaple1[1]) not in extracted_couples:
                for question in questions:
                    if generate_qa(question, pentaple[0], pentaple1[1], 'no') == 0:
                        pass
                    else:
                        f.write(str(generate_qa(question, pentaple[0], pentaple1[1], 'no')) + '\t' + relation + '\t"' + pentaple[2] + '"\t' + pentaple[3] + '\t' + pentaple1[4] + '\n')
            else:
                for question in questions:
                    f.write(str(generate_qa(question, pentaple[0], pentaple1[1], 'yes')) + '\t' + relation + '\t"' + pentaple[2] + '"\t' + pentaple[3] + '\t' + pentaple1[4] + '\n')




