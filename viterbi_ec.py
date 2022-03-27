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
Extra Credit: Here should be your best version of viterbi, 
with enhancements such as dealing with suffixes/prefixes separately
"""

def viterbi_ec(train, test):
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
    smooth_constant = 0.00001
    laplace = 0.00001
    word_types = ["NOUN", "ADV", "VERB", "ADJ"]
    
    for sentence in train :
        for data in sentence :
            word, tag = data

            if word not in final_tags :
                final_tags[word] = {}

            if tag not in final_tags[word] :
                final_tags[word][tag] = 1
            else:
                final_tags[word][tag] += 1
            
            if tag not in tags :
                tags[tag] = 1
                list_of_i[tag] = start_i
                start_i += 1

            else :
                tags[tag] += 1

    res = {}
    for i in final_tags.keys() :
        if len(final_tags[i].keys()) == 1 :

            for j in final_tags[i].keys() :
                res_addition = res.get(j,0)
                res[j] = 1 + res_addition
    
    
    for i in final_tags.keys() :
        for j in final_tags[i].keys() :
            smooth_constant = smooth_helper(word_types, j)
        #     if j not in word_types:
	# 			# may need to change #
        #         smooth_constant = 0.15
        #     else:
        #         smooth_constant = 0.000001

            numerator = smooth_constant + final_tags[i][j]
            partial_den = (len(j) + 1) * smooth_constant 
            denominator = tags[j] + partial_den
            final_tags[i][j] = numerator / denominator
  
    max_tags = max(tags, key=tags.get)
    probs = np.zeros(start_i)
    probs_pairs = np.zeros((start_i, start_i))
    
    for sentence in train :
        check_bool = True
        len_sentence = range(len(sentence[:-1]))

        for info in len_sentence :
            word, tag = sentence[info]

            if check_bool == True :
                probs[list_of_i[tag]] += 1
                check_bool = False
	    
            addition_to_info = info + 1
            subseq = sentence[addition_to_info][1]

            curr = list_of_i[tag]
            next = list_of_i[subseq]
            probs_pairs[curr][next] += 1
    
    for itr in range(len(probs)) :
        denominator = len(train)/ + 1
        probs[itr] = probs[itr] / denominator

    for tag, ct in tags.items() :
        for itr in range(len(probs_pairs)) :
            numerator_part = probs_pairs[list_of_i[tag]][itr]
            numerator = numerator_part + laplace
            denominator = (laplace * (len(tags) + 1)) + ct

            probs_p = list_of_i[tag]
            probs_pairs[probs_p][itr] = numerator / denominator

    list_of_tags = []
    for tag in list_of_i.keys() :
        list_of_tags.append(tag)

    to_return = []
    for sentence in test :
        trell = trellis(final_tags, tags, sentence, list_of_tags, probs, smooth_constant, probs_pairs, max_tags, list_of_i, res)

        if len(trell) == 0 :
            to_return.append([])
            continue

        # backtracing
        back_trace_ret = []
        tuples = trell[len(trell) - 1]

        max_of_tuples = max(tuples)
        i = tuples.index(max_of_tuples)

        back_trace_ret.append(list_of_tags[i])
        prev = max(tuples)

        for i in range(len(trell)-1, 0, -1) : 
            prev1 = list_of_i[prev[1]]
        
            prev = trell[i - 1][prev1]
            back_trace_ret.insert(0, prev[1])

        max_of_tags = max(trell[0])[1]
        back_trace_ret[0] = max_of_tags

        append_to_ret = zip(sentence, back_trace_ret)
        to_return.append(list(append_to_ret))
    return to_return

def smooth_helper(word_types, tag) :
    if tag not in word_types :
        smooth_constant = .4
    else :
        smooth_constant = 0.000001
    return smooth_constant

def tag_helper(tag, smooth_constant, size_of_tag, res) :
    part_res = sum(res.values())
    list_of_res = 1 + part_res

    if tag in res :
        numerator = smooth_constant + res.get(tag)
        denominator = (smooth_constant * size_of_tag) + list_of_res

    else:
        numerator = smooth_constant
        denominator = (smooth_constant * size_of_tag) + list_of_res

    prob = numerator / denominator

    return prob

def trellis(final_tags, tags, sentence, list_of_tags, probs, smooth_constant, probs_pairs, max_tags, list_of_i, res) :
    result = []
    size_of_tag = len(tags) + 1

    word_types = ["NOUN", "ADV", "VERB", "ADJ"]
    
    for i in range(len(sentence)) :
        pair_list = []
        add_word = sentence[i]
        if i == 0 :
            if add_word in final_tags :
                trell_helper_0(list_of_i, final_tags, add_word, smooth_constant, tags, size_of_tag, probs, pair_list, max_tags)
            else :
                for tag in list_of_i.keys() :
                    smooth_constant = smooth_helper(word_types, tag)
                    prob = tag_helper(tag, smooth_constant, size_of_tag, res)

                    tmp_tup = (prob, tag)
                    pair_list.append(tmp_tup)
        else :
            probability = 0
            for tag in list_of_i.keys() :
                itr = list_of_i[tag]
                smooth_constant = smooth_helper(word_types, tag)
                for j in range(len(list_of_i)) :
                    probability = -sys.maxsize
                    if add_word in final_tags :
                        if tag in final_tags[add_word] :
                            probability = final_tags[add_word][tag]
                        else :
                            denominator = (smooth_constant * size_of_tag) * tags[max_tags]
                            probability = smooth_constant / denominator
				
                    else :
                        probability = tag_helper(tag, smooth_constant, size_of_tag, res)
			
                    probability = result[i - 1][itr][0]+ math.log(probs_pairs[itr][j]) + math.log(probability)
                    tmp_tup = (probability, list_of_tags[itr])

                    if itr == 0:
                        pair_list.append(tmp_tup)
                    elif (probability > pair_list[j][0]):
                        pair_list[j] = tmp_tup

                # trell_helper_not_0(list_of_i, add_word, final_tags, tag, smooth_constant, size_of_tag, tags, max_tags, res, result, i, itr, probs_pairs, list_of_tags, pair_list)

        result.append(pair_list)
    return result

# def trell_helper_not_0(list_of_i, add_word, final_tags, tag, smooth_constant, size_of_tag, tags, max_tags, res, result, i, itr, probs_pairs, list_of_tags, pair_list) :
#     for j in range(len(list_of_i)) :
#         probability = -sys.maxsize
#         if add_word in final_tags :
#             if tag in final_tags[add_word] :
#                 probability = final_tags[add_word][tag]
#             else:
#                 denominator = (smooth_constant * size_of_tag) * tags[max_tags]
#                 probability = smooth_constant / denominator
		
#         else:
#             probability = tag_helper(tag, smooth_constant, size_of_tag, res)
	
#         probability = result[i - 1][itr][0]+ math.log(probs_pairs[itr][j]) + math.log(probability)
	
#         tmp_tup = (probability, list_of_tags[itr])
#         if itr == 0:
#             pair_list.append(tmp_tup)
#         elif (probability > pair_list[j][0]):
#             pair_list[j] = tmp_tup
	
def trell_helper_0(list_of_i, final_tags, add_word, smooth_constant, tags, size_of_tag, probs, pair_list, max_tags) :
    probability = 0
    for tag in list_of_i.keys() :
        if tag not in final_tags[add_word] :
            denominator = (smooth_constant * size_of_tag) + tags[max_tags]
            probability = smooth_constant / denominator

            tmp_tup = (probability, tag)
            pair_list.append(tmp_tup)

        else:
            probability = final_tags[add_word][tag]

            partial_tmp = probability * probs[list_of_i[tag]]
            tmp_tup = (partial_tmp, tag)
            pair_list.append(tmp_tup)