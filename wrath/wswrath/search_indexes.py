from haystack import indexes
from wswrath.models import URL

class URLIndex(indexes.SearchIndex, indexes.Indexable):
  text = indexes.CharField(document=True, use_template=True)
  title = indexes.CharField(model_attr='title')
  url = indexes.CharField(model_attr='url')
  urltitle = indexes.CharField(model_attr='urltitle')
  
  def get_model(self):
    return URL
