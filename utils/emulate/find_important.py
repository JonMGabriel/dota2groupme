import re
import nltk
import sys
import json
import pdb
import emulate_util
from progressbar import ProgressBar


if(len(sys.argv) < 2):
    print "Enter a message history (JSON file)"
else:

    message_data = []

    with open(sys.argv[1]) as data_file:
        message_data = json.load(data_file)

    relationships = {}

    print "TOTAL MESSAGES"
    print len(message_data[:len(message_data)/1])

    pbar = ProgressBar(
        maxval=len(message_data[:len(message_data)/1]),
    )


    for index, message in pbar(enumerate(message_data[:len(message_data)/1])):
        text = message["text"]
        time = message["created_at"]
        if index == (len(message_data) - 1):
            break #we hit the last message!
        previous_message = message_data[index + 1]


        response_time = time - previous_message["created_at"]
        if response_time > 50 or previous_message["text"] == None or text == None or message["user_id"] == 219313 or previous_message["user_id"] == 219313 or text.find("#") != -1:
            #print "Found one - " + previous_message["text"] + " -> " + text
            continue
            #the next message might not have been tied to this one or one of the messages was blank
            #also ignore all messages responding to sUN or from sUN

        message_weight = {}
        previous_message_weight = {}

        #Find Important words
        message_weight_temp = emulate_util.key_words(text)
        previous_message_weight_temp = emulate_util.key_words(previous_message["text"])

        #Add Type of Speech
        message_weight_pos = nltk.pos_tag(nltk.word_tokenize(text))
        previous_message_weight_pos = nltk.pos_tag(nltk.word_tokenize(previous_message["text"]))

        for word in message_weight_temp:
            for word_with_pos in message_weight_pos:
                if word == word_with_pos[0].lower():
                    message_weight[word + "#" + word_with_pos[1]] = message_weight_temp[word]

        for word in previous_message_weight_temp:
            for word_with_pos in previous_message_weight_pos:
                if word == word_with_pos[0].lower():
                    previous_message_weight[word + "#" + word_with_pos[1]] = previous_message_weight_temp[word]

        #pdb.set_trace()
        for result_key in message_weight:
            for next_key in previous_message_weight:
                #print next_key + " leads to " + result_key

                if next_key not in relationships:
                    relationships[next_key] = {}
                if result_key not in relationships[next_key]:
                    relationships[next_key][result_key] = 0
                #pdb.set_trace()
                relationships[next_key][result_key] += message_weight[result_key]
                #relationships[next_key][result_key] += 1

    with open("relationships.json", 'w') as outfile:
        json.dump(relationships, outfile)

    print "Number of Unique Relationships:"
    print len(relationships)
