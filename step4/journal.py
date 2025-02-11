from model.journal import Journal
from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers


class Journal_serializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = '__all__'

class Journal_viewset(ModelViewSet):
    queryset = Journal.objects.all()[:20]
    serializer_class = Journal_serializer

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs