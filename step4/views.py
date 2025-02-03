from django.shortcuts import render
from rest_framework.decorators import api_view
from model.article import Article
from django.contrib.auth.decorators import login_required


@login_required
@api_view(['GET'])
def migrate_to_step4(request):
    context = {
        'heading' : 'Message',
        'message' : 'No pending article found to migrate to Step 4'
    }

    # Fetch all files that need to be processed from Article table
    articles = Article.objects.filter(
        last_status__in=('active', 'failed'),
        provider__in_production=True, 
        last_step=3
        )

    print("Total article to ready to be processed in step 4 :", articles.count())


    context = {
            'heading' : 'Message',
            'message' : f'''{articles.count()} valid articles from step 3 to be migrated to Step 4. (work in progress ....)'''
        }

    return render(request, 'common/dashboard.html', context=context)

