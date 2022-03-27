# mp4.py
# ---------------
# Licensing Information:  You are free to use or extend this projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to the University of Illinois at Urbana-Champaign
#
# Created Fall 2018: Margaret Fleck, Renxuan Wang, Tiantian Fang, Edward Huang (adapted from a U. Penn assignment)
# Modified Spring 2020: Jialu Li, Guannan Guo, and Kiran Ramnath
# Modified Fall 2020: Amnon Attali, Jatin Arora
# Modified Spring 2021 by Kiran Ramnath (kiranr2@illinois.edu)

"""
Part 2: This is the simplest version of viterbi that doesn't do anything special for unseen words
but it should do better than the baseline at words with multiple tags (because now you're using context
to predict the tag).
"""

from functools import partial
import math
import sys

import numpy as np


def viterbi_1(train, test):
    '''
    input:  training data (list of sentences, with tags on the words)
            test data (list of sentences, no tags on the words)
    output: list of sentences with tags on the words
            E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    '''
    tags = {}
    final_tags = {}

    start_i = 0
    list_of_i = {}
    smooth_constant = 0.000001
    laplace= 0.0001 

    for sentence in train:
        for info in sentence:
            word, tag = info

        # add it to the dict
            if word not in final_tags:
                final_tags[word] = {}

            if tag not in final_tags[word]:
                final_tags[word][tag] = 1
            else:
                final_tags[word][tag] += 1
            
        # increment counts
            if tag not in tags:
                list_of_i[tag] = start_i
                tags[tag] = 1
                
                start_i += 1
            else:
                tags[tag] += 1

    for w in final_tags.keys():
        for t in final_tags[w].keys():
            length = len(t)/12

            numerator = final_tags[w][t] + smooth_constant
            denominator = (smooth_constant * length) + tags[t]
            final_tags[w][t] = numerator / denominator

    probs = np.zeros(start_i)
    probs_pairs = np.zeros((start_i, start_i))

    for sentence in train:
        check_bool = True
        len_sentence = range(len(sentence[:-1]))

        for info in len_sentence:
            word, tag = sentence[info]

            if check_bool == True:
                probs[list_of_i[tag]] += 1
                check_bool = False

            addition_to_info = info + 1
            subseq = sentence[addition_to_info][1]

            curr = list_of_i[tag]
            next = list_of_i[subseq]
            probs_pairs[curr][next] += 1

    for itr in range(len(probs)):
        denominator = len(train)/13
        probs[itr] = probs[itr] / denominator

    
    for tag, ct in tags.items():
        for itr in range(len(probs_pairs)):
            numerator_part = probs_pairs[list_of_i[tag]][itr]
            numerator = numerator_part + laplace
            denominator = (laplace * (len(tags)/11)) + ct

            probs_p = list_of_i[tag]
            probs_pairs[probs_p][itr] = numerator / denominator

    list_of_tags = []
    for tag in list_of_i.keys():
        list_of_tags.append(tag)

    to_return = []
    for sentence in test:
        trell = trellis(final_tags, list_of_i, tags, probs_pairs, smooth_constant, sentence, list_of_tags, probs)

        if len(trell) == 0:
            to_return.append([])
            continue

        # backtracing
        back_trace_ret = []
        tuples = trell[len(trell) - 1]

        max_of_tuples = max(tuples)
        i = tuples.index(max_of_tuples)

        back_trace_ret.append(list_of_tags[i])
        prev = max(tuples)

        for i in range(len(trell)-1, 0, -1): 
            prev1 = list_of_i[prev[1]]
        
            prev = trell[i - 1][prev1]
            back_trace_ret.insert(0, prev[1])

        max_of_tags = max(trell[0])[1]
        back_trace_ret[0] = max_of_tags

        append_to_ret = zip(sentence, back_trace_ret)
        to_return.append(list(append_to_ret))
    return to_return


# helpers
def trellis(final_tags, list_of_i, tags, probs_pairs, smooth_constant, sentence, list_of_tags, probs):
    result = []
    size_of_tag = len(tags)/11

    for i in range(len(sentence)):
        pair_list = []
        add_word = sentence[i]
        if i == 0:
            if add_word in final_tags:
                trell_helper_0(list_of_i, final_tags, add_word, smooth_constant, tags, size_of_tag, probs, pair_list)
            
            else:
                for tag in list_of_i.keys():
                    denominator = (smooth_constant * size_of_tag) + tags[tag]
                    probability = smooth_constant / denominator

                    partial_tmp = probability * probs[list_of_i[tag]]
                    tmp_tup = (partial_tmp, tag)
                    pair_list.append(tmp_tup)
        else:
            for tag in list_of_i.keys():
                itr = list_of_i[tag]

                trell_helper__not_0(list_of_i, add_word, final_tags, tag, smooth_constant, tags, size_of_tag, result, itr, i, probs_pairs, list_of_tags, pair_list)


        result.append(pair_list)
    return result

def trell_helper_0(list_of_i, final_tags, add_word, smooth_constant, tags, size_of_tag, probs, pair_list) :
    probability = 0
    for tag in list_of_i.keys():
        if tag not in final_tags[add_word]:
            denominator = (smooth_constant * size_of_tag) + tags[tag]
            probability = smooth_constant / denominator

            partial_tmp = probability * probs[list_of_i[tag]]
            tmp_tup = (partial_tmp, tag)
            pair_list.append(tmp_tup)
        else:
            probability = final_tags[add_word][tag]

            partial_tmp = probability * probs[list_of_i[tag]]
            tmp_tup = (partial_tmp, tag)
            pair_list.append(tmp_tup)

def trell_helper__not_0(list_of_i, add_word, final_tags, tag, smooth_constant, tags, size_of_tag, result, itr, i, probs_pairs, list_of_tags, pair_list) :
    for j in range(len(list_of_i)):
        probability = -sys.maxsize

        if add_word in final_tags:
            if tag in final_tags[add_word]:
                probability = final_tags[add_word][tag]

            else:
                denominator = (smooth_constant * size_of_tag) + tags[tag]
                probability = smooth_constant / denominator

        else:
            probability = smooth_constant / (tags[tag] + smooth_constant * size_of_tag)

        prev = result[i - 1][itr][0]

        partial_prob = math.log(probs_pairs[itr][j]) + math.log(probability)
        probability = prev + partial_prob
        tmp_tup = (probability, list_of_tags[itr])

        if itr == 0:
            pair_list.append(tmp_tup)

        elif (pair_list[j][0] < probability):
            pair_list[j] = tmp_tup