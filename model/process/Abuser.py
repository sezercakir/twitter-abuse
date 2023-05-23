class Abuser:
  def __init__(self, id, topic_count_dict, total_hub_topic_number, text_count_dict, not_abuser_flag):
    self.id = id
    self.topic_count_dict = topic_count_dict
    self.total_hub_topic_number = total_hub_topic_number
    self.text_count_dict = text_count_dict
    self.not_abuser_flag = not_abuser_flag

class TextCalculation:
  def __init__(self, name):
    self.name = name
    self.indices = None
    self.tfidf_Score_list = None
    self.word_count = 0