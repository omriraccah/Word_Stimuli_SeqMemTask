import random
import os
try: import xmljson
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'xmljson'])
    import abc
from xmljson import badgerfish as bf
try: import xml.etree.ElementTree
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'xml.etree.ElementTree'])
    import abc
from xml.etree.ElementTree import fromstring
try: import pydub
except ImportError:
    from pip._internal import main as pip
    pip(['install', '--user', 'pydub'])
    import abc
from pydub import AudioSegment
import csv
import math

# root_dir = "C:/Users/Michael/Documents/Academia/Studies/Event Segmentation/"

root_dir = os.path.dirname(os.path.abspath(__file__)).replace('\\','/') + "/"

# text_filename = "good_words.txt"
text_filename = "words.txt"
music_xml = ["melody 1.xml",
             "melody 2.xml",
             "melody 3.xml",
             "melody 4.xml",
             "melody 5.xml",
             "melody 6.xml",
             "melody 7.xml",
             "melody 8.xml",
             "melody 9.xml",
             "melody 10.xml",
             "melody 11.xml",
             "melody 12.xml",
             "melody 13.xml",
             "melody 14.xml",
             "melody 15.xml",
             "melody 16.xml",
             "melody 17.xml",
             "melody 18.xml",
             "melody 19.xml",
             "melody 20.xml",
             "melody 21.xml",
             "melody 22.xml",
             "melody 23.xml",
             "melody 24.xml",
             "melody 25.xml"]
word_file = open(root_dir + text_filename, 'r')
word_list = [line.replace('\n','') for line in word_file.readlines()]


def gen_timestamp():
    from datetime import datetime

    # datetime object containing current date and time
    now = datetime.now()

    print("now =", now)

    # dd/mm/YY H:M:S
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    return dt_string


def random_word_order(length,source):
    rand_list = []
    while len(rand_list)<length:
        def rand_word():
            id = random.randint(0, len(source)-1)
            if source[id] in rand_list: return rand_word();
            else: return source[id];
        rand_list.append(rand_word())
    #uncomment once we have enough words
    # for word in rand_list:
    #     source.remove(word)
    return rand_list

def random_melody_order(length,source):
    rand_list = []
    while len(rand_list)<length:
        def rand_file():
            id = random.randint(0, len(source)-1)
            if source[id] in rand_list: return rand_file();
            else: return source[id];
        rand_list.append(rand_file())
    for word in rand_list:
        source.remove(word)
    return rand_list

def parse_melody(xml_filename):
    transposition = random.randint(-6, 0)
    with open(root_dir + "melodies/" + xml_filename, 'r') as content_file:
        xml_file = content_file.read()
    xml_data = bf.data(fromstring(xml_file))
    xml_measures = xml_data['score-partwise']['part']['measure']
    pitch_dict = {'C':0,'C#':1, 'Db':1, 'D':2, 'D#':3,'Eb':3, 'E':4, 'F':5, 'F#':6, 'G':7, 'G#':8, 'Ab':8, 'A':9,'A#':10,'Bb':10,'B':11}
    melodies = {
        1: [],
        2: [],
        3: [],
        4: [],
        "transposition": transposition
    }
    for measure in xml_measures:
        for note in measure["note"]:
            try:
                voice = note["voice"]["$"]
                pitch_class= pitch_dict[note["pitch"]["step"]["$"]]
                octave = note["pitch"]["octave"]["$"]
                octave_offset = ((octave-1)*12)-4

                if ('alter' in note["pitch"]):
                    alter = note["pitch"]["alter"]["$"]
                else: alter = 0
                parsed = pitch_class + octave_offset + alter + transposition

                melodies[voice].append(parsed)
            except:
                continue
    return melodies
def generate_audio(melody,words, file_postfix, full_path):
    harmony = []
    for voice in melody:
        full_voice = AudioSegment.silent(duration=1)
        clips = []
        silences = []
        # print(melody[voice])
        for id in enumerate(melody[voice]):
            clip_name = words[id[0]].capitalize() + "_" + str(melody[voice][id[0]]) + ".wav"
            path = root_dir + "word_wavs/" + clip_name
            clip = AudioSegment.from_wav(path)
            pad_with_silence = AudioSegment.silent(duration=1500-len(clip))
            silences.append(len(pad_with_silence))
            clip = clip + pad_with_silence
            if(voice!=1):
                clip = clip-6
            clips.append(clip)
            full_voice = full_voice + clip
        harmony.append(full_voice)
    combined_voices = AudioSegment.silent(duration=len(harmony[0]))
    for voice in harmony:
        combined_voices = combined_voices.overlay(voice)

    combined_voices.export(full_path + "block_" + str(file_postfix) + ".mp3", format="mp3")



block_in_task = 25

def gen_task():
    participant_id = input("Enter participant ID, name, or other identifier: ")
    os.mkdir(root_dir + "task_sets/" + participant_id)
    xmls = random_melody_order(block_in_task,music_xml)
    timestamp = gen_timestamp()

    for i in range(block_in_task):
        print("Parsing melody " + str(i+1))
        melody = parse_melody(xmls[i])
        words = random_word_order(len(melody[1]),word_list)
        # words = random_word_order(25, word_list)
        # print(words,xmls[i])
        def gen_word_output(filename):
            dict_data = []
            formatted_words = []
            formatted_words.append("XML_file: " + filename + "\tTransposition: " + str(melody["transposition"]) + "\tDate/Time: " + timestamp + "\tParticipant ID: " + participant_id + "\n\n" + "TASK DATA: " + "\n\n")
            prefix = ""
            for i, word in enumerate(words):
                dict_entry = {"id":i+1, "phrase_no": math.ceil((i+1)/8), "pos_in_phrase": (i%8)+1, "word": word, "xml": filename, "transposition": str(melody["transposition"]), "participant": participant_id}
                if (i % 8 == 0 or i % 8 == 1):
                    prefix = "TT"
                    dict_entry["function"] = "t"
                elif (i % 8 == 6 or i % 8 == 7):
                    prefix = "DD"
                    dict_entry["function"] = "d"
                else:
                    prefix = "xx"
                    dict_entry["function"] = "x"
                formatted_words.append(("0" + str(i + 1))[-2:] + " - " + prefix + " - " + word + "\n")
                if (i % 8 == 7):
                    formatted_words.append("------------------------------\n")
                dict_data.append(dict_entry)
            return formatted_words,dict_data
        def gen_csv_output(dict_data):
            csv_columns = ['id', 'phrase_no', 'pos_in_phrase', 'word', 'function', 'xml', 'transposition','participant']
            csv_file = root_dir + "Task_sets/" + participant_id + "/block_" + str(i) + ".csv"
            try:
                with open(csv_file, 'w') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                    writer.writeheader()
                    for data in dict_data:
                        writer.writerow(data)
            except IOError:
                print("I/O error")
            return
        output_txt,output_dict = gen_word_output(xmls[i])
        del melody["transposition"]

        gen_word_file = open(root_dir + "Task_sets/" + participant_id + "/block_" + str(i) + ".txt", "w")
        gen_word_file.writelines(output_txt)
        gen_word_file.close()  # to change file access modes
        gen_csv_output (output_dict)
        generate_audio(melody,words,i,root_dir + "Task_sets/" + participant_id + "/")
gen_task()










