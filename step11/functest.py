from django.http import HttpResponse
from model.article import Article
from django.utils import timezone
from rest_framework.decorators import api_view

# Update last step of the articles in step 10
@api_view(['GET'])
def update_step(request):
    # Get articles to promote from step 10 to 11
    articles = Article.objects.filter(
        last_status='active',
        provider__in_production=True,
        last_step=10,
        provider__article_switch=True
    )
    
    # Update step and end_date
    articles.update(last_step=11, end_date=timezone.now())

    ###################
    # articles = articles.exclude(journal__collection_status='from_submission')
    ###################

    ###################
    articles = Article.objects.filter(
        last_step=11
    ).exclude(import_type__endswith='usda')
    articles.update(last_status='completed', end_date=timezone.now())

    ####################
    return HttpResponse("done")
