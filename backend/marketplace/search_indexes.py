from haystack import indexes
from oscar.core.loading import get_model

Product = get_model('catalogue', 'Product')

class ProductIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    description = indexes.CharField(model_attr='description', null=True)
    price = indexes.FloatField(model_attr='price', null=True)
    instant_delivery = indexes.BooleanField(model_attr='instant_delivery', default=False)
    
    def get_model(self):
        return Product
    
    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_public=True)
