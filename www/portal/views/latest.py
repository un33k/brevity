
from .search import ArticleSearchView


class ArticleLatestView(ArticleSearchView):
    """
    Article Latest View
    """
    url_path = 'latest'

    def get_data(self):
        data = super(ArticleLatestView, self).get_data()
        data['referrer'] = 'latest'
        return data
