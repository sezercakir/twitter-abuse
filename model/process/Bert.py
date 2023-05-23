import sys
from difflib import SequenceMatcher
import networkx as nx
import pandas as pd
from model.process.Abuser import Abuser
from model.utils import get_stop_words, clean_text
from model.Settings import Settings
from bertopic.backend import BaseEmbedder
from bertopic.cluster import BaseCluster
from bertopic.vectorizers import ClassTfidfTransformer
from bertopic.dimensionality import BaseDimensionalityReduction
from sklearn.feature_extraction.text import CountVectorizer
from bertopic import BERTopic
import statistics


class Bert(Settings):

    def __init__(self):
        super().__init__()
        self.abuser_from_selection2 = None
        self.stop_words_tr = get_stop_words()
        self.abuser_candidates_df = None
        self.all_df = None

    def construct_graph(self, topics, one_frame, df_all):
        self.all_df = one_frame
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

    def apply_bertopic(self):

        self.abuser_candidates_df['clean_text'] = self.abuser_candidates_df.text.apply(clean_text)
        self.all_df['clean_text'] = self.all_df.text.apply(clean_text)

        cand_list_5 = self.abuser_candidates_df.clean_text.to_list()
        all_tweets_list = self.all_df.clean_text.to_list()
        self.all_df.Topic = pd.Categorical(self.all_df.Topic)
        self.all_df['topiccode'] = self.all_df.Topic.cat.codes
        y_ = self.all_df["topiccode"].values.tolist()

        tw_ids = self.abuser_candidates_df['tw_id'].unique()
        path_candidates_5_last = self.abuser_candidates_df.drop_duplicates(subset='tw_id', keep='last')

        for id_ in tw_ids:
            hub_connections = self.abuser_candidates_df[self.abuser_candidates_df['tw_id'] == id_]['Topic'].to_list()
            split_list = [item.split() for item in hub_connections]
            hub_connections = [item for sublist in split_list for item in sublist]

            index = path_candidates_5_last[path_candidates_5_last['tw_id'] == id_].index[0]
            path_candidates_5_last['Topic'] = path_candidates_5_last['Topic'].astype('object')
            path_candidates_5_last.at[index, 'Topic'] = hub_connections

        cand_list_5_final = path_candidates_5_last
        cand_list_5_final.reset_index(drop=True, inplace=True)

        vectorizer_model = CountVectorizer(stop_words=self.stop_words_tr)
        # Prepare our empty sub-models and reduce frequent words while we are at it.
        empty_embedding_model = BaseEmbedder()
        empty_dimensionality_model = BaseDimensionalityReduction()
        empty_cluster_model = BaseCluster()
        ctfidf_model = ClassTfidfTransformer(reduce_frequent_words=True)

        # Fit BERTopic without actually performing any clustering
        topic_model_5 = BERTopic(
            language="turkish",
            umap_model=empty_dimensionality_model,
            hdbscan_model=empty_cluster_model,
            ctfidf_model=ctfidf_model,
            vectorizer_model=vectorizer_model,
            calculate_probabilities=True
        )
        topics, probs = topic_model_5.fit_transform(all_tweets_list, y=y_)
        topic_counts = max(topic_model_5.get_topic_info().groupby('Topic')['Count'].sum().index) + 1

        abuser_list = []
        for candidates_index in range(cand_list_5_final.shape[0]):
            topics_of_candidates = cand_list_5_final['Topic'][candidates_index]
            topics_of_candidates = [item.lower() for item in
                                    topics_of_candidates]  # converte to all topics to lowercase for further comparisons
            tweet = cand_list_5_final['clean_text'][candidates_index]
            splitted_tweet = tweet.split()
            topic_count_dict = {key: 0 for key in
                                range(topic_counts)}  # key as bertopic topic index, value as hub count in that topic
            text_count_dict = {key: 0 for key in range(topic_counts)}
            not_abuser_flag = None
            # topic calculation
            for t_i in range(topic_counts):
                bert_topics_list = [tuple_topic[0] for tuple_topic in topic_model_5.get_topic(t_i)]
                same_topic_count = len(set(topics_of_candidates).intersection(bert_topics_list))
                # text calculation
                same_word_count = len(set(splitted_tweet).intersection(bert_topics_list))
                indices = [index for index, item in enumerate(bert_topics_list) if item in splitted_tweet]

                if len(indices) > 3:
                    count = len([num for num in indices if 0 < num < 5])
                    if count >= 3:
                        not_abuser_flag = True
                        break

                topic_count_dict[t_i] = same_topic_count
                text_count_dict[t_i] = same_word_count

            abuser_list.append(Abuser(cand_list_5_final['author_id'][candidates_index], topic_count_dict,
                                      len(topics_of_candidates), text_count_dict, not_abuser_flag))

        # find abuser from topic information
        abuser_ids_from_topic = list()

        for abuser_cand in abuser_list:
            if abuser_cand.not_abuser_flag:
                continue

            topic_count_list = list(abuser_cand.topic_count_dict.values())
            if(len(topic_count_list)==1):
                continue
            std_of_topic_count = statistics.stdev(topic_count_list)
            nonzero_count = len(list(filter(lambda x: x != 0, topic_count_list)))
            max_topic_count = max(topic_count_list)

            if max_topic_count == round(len(topic_count_list) / 2) or std_of_topic_count > 0.4:
                continue
            # evenly distributed or almost evenly distributed -> abuser
            if std_of_topic_count <= 0.4:
                abuser_ids_from_topic.append(abuser_cand.id)
            if abuser_cand.total_hub_topic_number - 1 < nonzero_count:
                abuser_ids_from_topic.append(abuser_cand.id)

        abuser_ids_from_topic = list(set(int(x) for x in abuser_ids_from_topic))

        candidates_index = 0
        abuser_ids_from_text = list()
        for abuser_cand in abuser_list:
            if abuser_cand.id in abuser_ids_from_topic or abuser_cand.not_abuser_flag:
                candidates_index += 1
                continue
            text_count_values = list(abuser_cand.text_count_dict.values())
            nonzero_count = len(list(filter(lambda x: x != 0, text_count_values)))

            if nonzero_count >= abuser_cand.total_hub_topic_number:
                abuser_ids_from_text.append(abuser_cand.id)

        abuser_ids_final = abuser_ids_from_topic + list(set(int(x) for x in abuser_ids_from_text))

        return abuser_ids_final
