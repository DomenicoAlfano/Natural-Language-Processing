import re
from tqdm import tqdm


class Morph():
    def __init__(self, delta, train, test):
        self.words = None
        self.list_words_sequences = None
        self.list_morphemes_raw = None
        self.list_morphemes = None
        self.delta = delta
        self.train_file = train
        self.test_file = test
        # Data Loaded
        self.train_data = self.load_data(self.train_file)
        self.test_data = self.load_data(self.test_file)
        # Created Label
        self.training_label = self.label(self.train_data)
        self.testing_label = self.label(self.test_data)
        # Created Feature
        self.training_feature = self.features(self.train_data)
        self.testing_feature = self.features(self.test_data)

    # Create features for all the words
    def features(self, data):
        self.words = self.extract_word(data)
        self.list_words_sequences = self.all_words_sequence()
        feature = self.features_extraction()
        return feature

    # Create label for all the words
    def label(self, data):
        self.list_morphemes_raw = self.extract_morph(data)
        self.list_morphemes = self.clean_morphemes()
        list_label = []
        for feature in self.list_morphemes:
            list_label.append(self.add_tag_to_morph(feature))
        return list_label

    # Extract the list of world
    @staticmethod
    def extract_morph(data):
        list_morphemes = []
        pattern_coma = re.compile(r'\t(.+?),', flags=re.DOTALL)
        pattern1 = re.compile(r'\t(.+?):', flags=re.DOTALL)
        pattern2 = re.compile(r' (.+?):', flags=re.DOTALL)

        for line in data:
            morphims = []
            first_possibility = pattern_coma.findall(line)

            if len(first_possibility) > 0:
                line2 = first_possibility[0]
            else:
                line2 = line
            morph_1 = pattern1.findall(line)
            morph_n = pattern2.findall(line2)
            morphims.extend(morph_1)
            morphims.extend(morph_n)
            list_morphemes.append(morphims)
        return list_morphemes

    def clean_morphemes(self):
        list_morphemes = []
        for raw_morph in self.list_morphemes_raw:
            cleaned_morphemes = []
            for i in range(len(raw_morph)):
                for j in range(len(raw_morph)):
                    if (raw_morph[i] == raw_morph[j] or raw_morph[j] == '~') and i != j:
                        raw_morph[j] = 'DELETING'
            for word in raw_morph:
                if word != 'DELETING':
                    cleaned_morphemes.append(word)
            list_morphemes.append(cleaned_morphemes)
        return list_morphemes

    def add_tag_to_morph(self, morphemes):
        label = []
        label.append('START')
        for morph in morphemes:
            if len(morph) == 1:
                label.append('S')
            if len(morph) == 2:
                label.append('B')
                label.append('E')
            if len(morph) > 2:
                label.append('B')
                for i in range(1, len(morph) - 1):
                    label.append('M')
                label.append('E')
        label.append('STOP')
        return label

    def write(self, file, data):
        f = open(file, 'w')
        f.write(data)
        f.close()

    # Load Train

    def load_data(self, file):
        f = open(file, 'r')
        data = f.read()
        return data.split('\n')

    # Extrac the list of world
    def extract_word(self, data):
        list_word = []
        for line in data:
            temp_word = re.search('(.*)\t', line)
            if temp_word is not None:
                list_word.append(temp_word.group(1))
        return list_word

    # Create the zero feature set for the respectively delta
    def create_fetuare_zero_set(self):
        alfabeto = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'r', 't', 'u', 'v',
                    'w', 'x', 'y', 'z', '-', "'"]
        feature_zero_set = {}
        if self.delta >= 1:
            for char in alfabeto:
                feature_zero_set["L_" + char] = 0
                feature_zero_set["R_" + char] = 0
        if self.delta >= 2:
            for char1 in alfabeto:
                for char2 in alfabeto:
                    feature_zero_set["L_" + char1 + char2] = 0
                    feature_zero_set["R_" + char1 + char2] = 0
        if self.delta >= 3:
            for char1 in alfabeto:
                for char2 in alfabeto:
                    for char3 in alfabeto:
                        feature_zero_set["L_" + char1 + char2 + char3] = 0
                        feature_zero_set["R_" + char1 + char2 + char3] = 0
        return feature_zero_set

    # Extract all sequences of words
    def all_words_sequence(self):
        words_sequence = []
        for word in self.words:
            words_sequence.append(self.word_sequence_exctractor(word))
        return words_sequence

    # Given a word return the sequence form of it
    @staticmethod
    def word_sequence_exctractor(word):
        fracted_word = list(word)
        word_sequence = ["<w>"]
        for i in range(len(fracted_word)):
            word_sequence.append(fracted_word[i])
        word_sequence.append("</w>")
        return word_sequence

    # Given a word return the feature vector
    def word_features_extractor(self, sequence):
        character = []
        for i in range(len(sequence)):
            feature_zero = {}
            # feature_zero = self.create_feature_zero_set()
            feature_zero.update(self.character_feature(sequence, i))
            character.append({sequence[i]: feature_zero})
        return character

    # Given the sequence the position and delta return a feature
    # of the character selected
    def character_feature(self, sequence, pos):
        feature_one = {}
        for i in range(1, self.delta + 1):
            if self.right_features_set(sequence, pos, i) is not '':
                feature_one['R_' + self.right_features_set(sequence, pos, i)] = 1
            if self.left_features_set(sequence, pos, i) is not '':
                feature_one['L_' + self.left_features_set(sequence, pos, i)] = 1
        return feature_one

    @staticmethod
    def right_features_set(sequence, pos, delta):
        right_range = ''
        for i in range(delta):
            if pos + i < len(sequence):
                right_range += sequence[pos + i]
        return right_range

    @staticmethod
    def left_features_set(sequence, pos, delta):
        left_range = ''
        for i in reversed(range(1, delta + 1)):
            if pos - i >= 0:
                left_range += sequence[pos - i]
        return left_range

    def features_extraction(self):
        feature_data = []
        t = tqdm(range(len(self.list_words_sequences)), desc='Extracting', leave=True)
        for i in t:
            word_feature = self.word_features_extractor(self.list_words_sequences[i])
            feature_data.append(word_feature)
        return feature_data
