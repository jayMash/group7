import nltk
import yaml


class Splitter(object):
    def __init__(self):
        self.nltk_splitter = nltk.data.load('tokenizers/punkt/english.pickle')
        self.nltk_tokenizer = nltk.tokenize.TreebankWordTokenizer()

    def split(self, text):
        """
        input format: a paragraph of text
        output format: a list of lists of words.
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        """
        sentences = self.nltk_splitter.tokenize(text)
        tokenized_sentences = [self.nltk_tokenizer.tokenize(sent) for sent in sentences]
        return tokenized_sentences


class POSTagger(object):
    def __init__(self):
        pass
        
    def pos_tag(self, sentences):
        """
        input format: list of lists of words
            e.g.: [['this', 'is', 'a', 'sentence'], ['this', 'is', 'another', 'one']]
        output format: list of lists of tagged tokens. Each tagged tokens has a
        form, a lemma, and a list of tags
            e.g: [[('this', 'this', ['DT']), ('is', 'be', ['VB']), ('a', 'a', ['DT']), ('sentence', 'sentence', ['NN'])],
                    [('this', 'this', ['DT']), ('is', 'be', ['VB']), ('another', 'another', ['DT']), ('one', 'one', ['CARD'])]]
        """

        pos = [nltk.pos_tag(sentence) for sentence in sentences]
        #adapt format
        pos = [[(word, word, [postag]) for (word, postag) in sentence] for sentence in pos]
        return pos

class DictionaryTagger(object):
    def __init__(self, dictionary_paths):
        files = [open(path, 'r') for path in dictionary_paths]
        dictionaries = [yaml.load(dict_file) for dict_file in files]
        map(lambda x: x.close(), files)
        self.dictionary = {}
        self.max_key_size = 0
        for curr_dict in dictionaries:
            for key in curr_dict:
                if key in self.dictionary:
                    self.dictionary[key].extend(curr_dict[key])
                else:
                    self.dictionary[key] = curr_dict[key]
                    self.max_key_size = max(self.max_key_size, len(key))

    def tag(self, postagged_sentences):
        return [self.tag_sentence(sentence) for sentence in postagged_sentences]

    def tag_sentence(self, sentence, tag_with_lemmas=False):
        """
        the result is only one tagging of all the possible ones.
        The resulting tagging is determined by these two priority rules:
            - longest matches have higher priority
            - search is made from left to right
        """
        tag_sentence = []
        N = len(sentence)
        if self.max_key_size == 0:
            self.max_key_size = N
        i = 0
        while (i < N):
            j = min(i + self.max_key_size, N) #avoid overflow
            tagged = False
            while (j > i):
                expression_form = ' '.join([word[0] for word in sentence[i:j]]).lower()
                expression_lemma = ' '.join([word[1] for word in sentence[i:j]]).lower()
                if tag_with_lemmas:
                    literal = expression_lemma
                else:
                    literal = expression_form
                if literal in self.dictionary:
                    #self.logger.debug("found: %s" % literal)
                    is_single_token = j - i == 1
                    original_position = i
                    i = j
                    taggings = [tag for tag in self.dictionary[literal]]
                    tagged_expression = (expression_form, expression_lemma, taggings)
                    if is_single_token: #if the tagged literal is a single token, conserve its previous taggings:
                        original_token_tagging = sentence[original_position][2]
                        tagged_expression[2].extend(original_token_tagging)
                    tag_sentence.append(tagged_expression)
                    tagged = True
                else:
                    j = j - 1
            if not tagged:
                tag_sentence.append(sentence[i])
                i += 1
        return tag_sentence

def value_of(sentiment):
    if sentiment == 'positive': return 1
    if sentiment == 'negative': return -1
    return 0

def sentiment_score(review):
    return sum([sentence_score(sentence, None, 0.0) for sentence in review])

def sentence_score(sentence_tokens, previous_token, acum_score):
    if not sentence_tokens:
        return acum_score
    else:
        current_token = sentence_tokens[0]
        tags = current_token[2]
        token_score = sum([value_of(tag) for tag in tags])
        if previous_token is not None:
            previous_tags = previous_token[2]
            if 'inc' in previous_tags:
                token_score *= 2.0
            elif 'dec' in previous_tags:
                token_score /= 2.0
            elif 'inv' in previous_tags:
                if 'inv' in tags:
                    token_score += 1.0
                else:
                    token_score *= -1.0

        return sentence_score(sentence_tokens[1:], current_token, acum_score + token_score)
#################################################3

# text = """What can I say about this place. The staff of the restaurant is nice and the eggplant is not bad. Apart from that, very uninspired food, lack of atmosphere and too expensive. I am a staunch vegetarian and was sorely dissapointed with the veggie options on the menu. Will be the last time I visit, I recommend others to avoid."""
# text="""I am not awesome and cool"""
text = raw_input("=> ")
splitter = Splitter()
postagger = POSTagger()

splitted_sentences = splitter.split(text)
# print(splitted_sentences)
#[['What', 'can', 'I', 'say', 'about', 'this', 'place', '.'], ['The', 'staff', 'of', 'the', 'restaurant', 'is', 'nice', 'and', 'eggplant', 'is', 'not', 'bad', '.'], ['apart', 'from', 'that', ',', 'very', 'uninspired', 'food', ',', 'lack', 'of', 'atmosphere', 'and', 'too', 'expensive', '.'], ['I', 'am', 'a', 'staunch', 'vegetarian', 'and', 'was', 'sorely', 'dissapointed', 'with', 'the', 'veggie', 'options', 'on', 'the', 'menu', '.'], ['Will', 'be', 'the', 'last', 'time', 'I', 'visit', ',', 'I', 'recommend', 'others', 'to', 'avoid', '.']]

###################################################
pos_tagged_sentences = postagger.pos_tag(splitted_sentences)

# print(pos_tagged_sentences)
#[[('What', 'What', ['WP']), ('can', 'can', ['MD']), ('I', 'I', ['PRP']), ('say', 'say', ['VB']), ('about', 'about', ['IN']), ('this', 'this', ['DT']), ('place', 'place', ['NN']), ('.', '.', ['.'])], [('The', 'The', ['DT']), ('staff', 'staff', ['NN']), ('of', 'of', ['IN']), ('the', 'the', ['DT']), ('restaurant', 'restaurant', ['NN']), ('is', 'is', ['VBZ']), ('nice', 'nice', ['JJ']), ('and', 'and', ['CC']), ('eggplant', 'eggplant', ['NN']), ('is', 'is', ['VBZ']), ('not', 'not', ['RB']), ('bad', 'bad', ['JJ']), ('.', '.', ['.'])], [('apart', 'apart', ['NN']), ('from', 'from', ['IN']), ('that', 'that', ['DT']), (',', ',', [',']), ('very', 'very', ['RB']), ('uninspired', 'uninspired', ['VBN']), ('food', 'food', ['NN']), (',', ',', [',']), ('lack', 'lack', ['NN']), ('of', 'of', ['IN']), ('atmosphere', 'atmosphere', ['NN']), ('and', 'and', ['CC']), ('too', 'too', ['RB']), ('expensive', 'expensive', ['JJ']), ('.', '.', ['.'])], [('I', 'I', ['PRP']), ('am', 'am', ['VBP']), ('a', 'a', ['DT']), ('staunch', 'staunch', ['NN']), ('vegetarian', 'vegetarian', ['NN']), ('and', 'and', ['CC']), ('was', 'was', ['VBD']), ('sorely', 'sorely', ['RB']), ('dissapointed', 'dissapointed', ['VBN']), ('with', 'with', ['IN']), ('the', 'the', ['DT']), ('veggie', 'veggie', ['NN']), ('options', 'options', ['NNS']), ('on', 'on', ['IN']), ('the', 'the', ['DT']), ('menu', 'menu', ['NN']), ('.', '.', ['.'])], [('Will', 'Will', ['NNP']), ('be', 'be', ['VB']), ('the', 'the', ['DT']), ('last', 'last', ['JJ']), ('time', 'time', ['NN']), ('I', 'I', ['PRP']), ('visit', 'visit', ['VBP']), (',', ',', [',']), ('I', 'I', ['PRP']), ('recommend', 'recommend', ['VBP']), ('others', 'others', ['NNS']), ('to', 'to', ['TO']), ('avoid', 'avoid', ['VB']), ('.', '.', ['.'])]]

####################################################

dicttagger = DictionaryTagger([ 'dicts/positive_1.yml', 'dicts/negative_1.yml', 'dicts/inc.yml', 'dicts/dec.yml', 'dicts/inv.yml'])

dict_tagged_sentences = dicttagger.tag(pos_tagged_sentences)

# print(dict_tagged_sentences)
########################################################

sScore = sentiment_score(dict_tagged_sentences)
if sScore > 0:
    print"sentiment score = ", sScore, "\nPositive"
elif sScore < 0:
    print"sentiment score = ", sScore, "\nNegative"
else:
    print"sentiment score = ", sScore, "\nNeutral"


