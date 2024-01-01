import yake
import operator


class NLP:

    def __init__(self) -> None:
        self.UNIGRAM_PATH = "files/datasets/unigram_freq.csv"

    def get_common_keywords(self, text):
        keywords_tlp = self._get_keywords(text)

        keywords = []
        for word in keywords_tlp:
            keywords.append(word[0].split(" "))

        keywords = self._check_unigram_freq(keywords)
        return keywords

    def _get_keywords(self, text):
        ''' get keywords from text '''
        kw_extractor = yake.KeywordExtractor(
            n=2, dedupLim=0.4, dedupFunc='seqm')
        keywords = kw_extractor.extract_keywords(text)

        return keywords

    def _check_unigram_freq(self, keywords, max_items=5):
        '''
        checks how much the word is common word wide
        commons words will be great keywords for video and image search
        '''

        words = []
        with open(self.UNIGRAM_PATH, "r") as f:
            words = f.readlines()

        common_words = {}
        for word in words:
            word_splitted = word.split(",")[0].strip(" ").strip("\n")
            word_rating = word.split(",")[2].strip(" ").strip("\n")
            common_words[word_splitted] = word_rating

        selected_words = {}
        for keyword in keywords:

            if len(keyword) == 1:
                if keyword[0] in common_words:
                    selected_words[keyword[0]] = float(
                        common_words[keyword[0]])

            else:
                # list has two keywords
                if keyword[0] in common_words and keyword[1] in common_words:
                    avg_rating = (float(
                        common_words[keyword[0]]) + float(common_words[keyword[0]])) / 2
                    avg_rating = round(avg_rating, 5)
                    selected_words[keyword[0]+" "+keyword[1]] = avg_rating

        newlist = sorted(selected_words.items(), key=operator.itemgetter(1))

        result = []
        for i, word in enumerate(newlist):
            if i < max_items:
                result.append(word[0])

        return result
