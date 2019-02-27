########################################################################################################################
###### TRIPLE MAPPING, TIME ############################################################################################
########################################################################################################################

# for more comments look at the general version

import spacy
import pickle

print('loading model...')
nlp = spacy.load('en')
print('model loaded\n')

part = []
material = []
generalization = []
specialization = []
time = []
with open('patterns.tsv') as f:
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
    if x_flag == 1 and y_flag == 1:
        return final_question + '\t' + answer
    elif x_flag == 0 and y_flag == 1 and answer == 'yes':
        return final_question + '\t' + subj
    elif x_flag == 1 and y_flag == 0 and answer == 'yes':
        return final_question + '\t' + obj
    else:
        return 0

r1 = 'is made from'  # double seed
r2 = 'is made of'
questions = list(material)
relation = 'material'
simil_threshold = 0.9
print('seed :\t', r1)
path = "triples_folder_0-180.p"
path1 = "triples_folder_180-360.p"
I = pickle.load( open( path, "rb" ) ) + pickle.load( open( path1, "rb" ) )


def sim(pi1, pi2):
    doc1 = nlp(u'X ' + pi1 + ' Y')
    doc2 = nlp(u'X ' + pi2 + ' Y')

    shortest_path_1 = list(doc1[-1].ancestors)
    shortest_path_2 = list(doc2[-1].ancestors)

    dep_pi_sp1 = [doc1[0].dep_] + [w.dep_ for w in shortest_path_1] + [doc1[-1].dep_]
    dep_pi_sp2 = [doc2[0].dep_] + [w.dep_ for w in shortest_path_2] + [doc2[-1].dep_]
    if dep_pi_sp1 != dep_pi_sp2:
        return 0
    elif str(doc2[1]) in [',', ')', "'", "''", ':'] or 'and' in pi2:
        return 0
    else:
        similarity = 0
        num_words = len(shortest_path_1)
        for i in range(num_words):
            similarity += shortest_path_1[i].similarity(shortest_path_2[i])
        if shortest_path_1[-1].lemma_ in ['have', 'be', 'take'] and shortest_path_2[-1].lemma_ in ['have', 'be', 'take']:
            similarity += num_words * shortest_path_1[-2].similarity(shortest_path_2[-2])
        else:
            similarity += num_words * shortest_path_1[-1].similarity(shortest_path_2[-1])
        similarity /= (2 * num_words)

        return round(similarity, 3)

print('similarity threshold', simil_threshold, '\n')
extracted_couples = []
full_extracted_pentaples = []
for item in I:
    simil = sim(r1, item[1])
    if simil >= simil_threshold:
        if (item[0], item[2]) not in extracted_couples:
            extracted_couples.append((item[0], item[2]))
            full_extracted_pentaples.append((item[0], item[2], item[3], item[4], item[5]))
            # print(item[0] + '\t' + 'material' + '\t' + item[2])
    simil = sim(r2, item[1])
    if simil >= simil_threshold:
        if (item[0], item[2]) not in extracted_couples:
            extracted_couples.append((item[0], item[2]))
            full_extracted_pentaples.append((item[0], item[2], item[3], item[4], item[5]))

f = open('question-answer-pairs.txt', 'a', encoding='utf-8')

for pentaple in full_extracted_pentaples:
    for question in questions:
        f.write(str(generate_qa(question, pentaple[0], pentaple[1], 'yes')) + '\t' + relation + '\t"' + pentaple[2] + '"\t' + pentaple[3] + '\t' + pentaple[4] + '\n')
    for pentaple1 in full_extracted_pentaples:
        if (pentaple[0], pentaple1[1]) not in extracted_couples:
            for question in questions:
                if generate_qa(question, pentaple[0], pentaple1[1], 'no') == 0:
                    pass
                else:
                    f.write(str(generate_qa(question, pentaple[0], pentaple1[1], 'no')) + '\t' + relation + '\t"' + pentaple[2] + '"\t' + pentaple[3] + '\t' + pentaple1[4] + '\n')
        else:
            for question in questions:
                f.write(str(generate_qa(question, pentaple[0], pentaple1[1], 'yes')) + '\t' + relation + '\t"' + pentaple[2] + '"\t' + pentaple[3] + '\t' + pentaple1[4] + '\n')




