
from django.shortcuts import render
from model.article import Article
import pickle

def test(request):
    context = {
        'heading' : 'Message',
        'message' : 'done'
    }
        
    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=7
        # article_switch = True
        ).exclude(journal=None)
    
    for article in articles:
        try:
            with open(article.citation_pickle.path, 'rb') as file:
                cit = pickle.load(file)
                print(cit.local.identifiers['handle'])
        except Exception as e:
            continue

    return render(request, 'common/dashboard.html', context=context)
    