import sys
from difflib import SequenceMatcher
import networkx as nx
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer
from model.utils import get_stop_words
from model.Settings import Settings


class Bert(Settings):

    def __init__(self):
        super().__init__()
        self.abuser_from_selection2 = None
        self.stop_words_tr = get_stop_words()
        self.abuser_candidates_df = None

    def construct_graph(self, topics, one_frame, df_all):
        num_topics = len(topics)
        graph = nx.Graph()
        for topic in topics:
            graph.add_node(topic, node_type="Hub")

        for row in df_all:
            graph.add_node(row['tw_id'], node_type="Tweet", tweet_id=row['tw_id'],
                           auth_id=row['author_id'], text=row['text'], abuse=row['abuser'])
            graph.add_edge(row['Topic'], row['tw_id'])

        degree_dict = dict(graph.degree())
        nx.set_node_attributes(graph, degree_dict, 'degree')  # G.nodes(data='degree') accessing it
        abuser_candidates = sorted(degree_dict, key=degree_dict.get, reverse=True) \
            [num_topics:self.selected_candidate_num_upper_bound]

        self.abuser_candidates_df = one_frame.loc[(one_frame['tw_id'].isin(abuser_candidates)) &
                                               (one_frame['abuser'] == False)]

    def detect_abuser_selection2(self):
        """

        :return:
        """
        detected_abuser = 0
        abusers = list()
        self.abuser_candidates_df.index = range(0, self.abuser_candidates_df.shape[0])
        for i in range(self.abuser_candidates_df.shape[0]):
            text_tw = self.abuser_candidates_df['text'][i]
            for j in range(i + 1, self.abuser_candidates_df.shape[0]):
                ratio = SequenceMatcher(None, text_tw, self.abuser_candidates_df['text'][j]).ratio()
                if ratio > 0.94 and self.abuser_candidates_df['Topic'][i] == self.abuser_candidates_df['Topic'][j] and \
                        self.abuser_candidates_df['author_id'][i] == self.abuser_candidates_df['author_id'][j]:
                    print("Abuser DETECTED 2", file=sys.stderr)
                    detected_abuser += 2
                    abusers.append(self.abuser_candidates_df['author_id'][i])
                    abusers.append(self.abuser_candidates_df['author_id'][j])

        return list(set(abusers))

    def apply_bertopic(self, frame):
        candidates = self.abuser_candidates_df.clean_text.to_list()
        all = frame.clean_text.to_list()

        vectorizer_model = CountVectorizer(stop_words=self.stop_words_tr)

        topic_model_5 = BERTopic(language="turkish", vectorizer_model=vectorizer_model)
        topics, prob = topic_model_5.fit_transform(all)

        abuser_list = list()
        # selection 3 part
        return abuser_list

