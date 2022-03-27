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
# Modified Spring 2021 by Kiran Ramnath
"""
Part 1: Simple baseline that only uses word statistics to predict tags
"""
from collections import Counter


def baseline(train, test):
    '''
    input:  training data (list of sentences, with tags on the words)
            test data (list of sentences, no tags on the words)
    output: list of sentences, each sentence is a list of (word,tag) pairs.
            E.g., [[(word1, tag1), (word2, tag2)], [(word3, tag3), (word4, tag4)]]
    '''

    tags = {}
    final_tags = {}

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

        #     increment count
            if tag not in tags:
                tags[tag] = 1
            else:
                tags[tag] += 1

    max_tags = max(tags, key=tags.get)
    result = []

    for sentence in test:
        list_of_word_pairs = []

        for word in sentence:
            if word in final_tags:
                tag = max(final_tags[word], key=final_tags[word].get)
                list_of_word_pairs.append((word, tag))

            else:
                # handles the unseen words
                list_of_word_pairs.append((word, max_tags))

        result.append(list_of_word_pairs)

    return result
