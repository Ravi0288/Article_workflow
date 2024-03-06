from rest_framework.decorators import api_view
from rest_framework.response import Response
from .wrapper import *


@timer
@api_view(['GET'])
def trigger_steps(request):
    return Response("All steps executed successfully.")