from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from model.archive import Archive

    

# serializer for Archive model
class Archive_serializers(ModelSerializer):
    class Meta:
        model = Archive
        fields = '__all__'


# views for Archive
class Archive_view(ModelViewSet):
    queryset = Archive.objects.all().order_by("-id")[:10]
    serializer_class = Archive_serializers

    def get_queryset(self):
        qs = super().get_queryset()
        params = self.request.GET
        qs = qs.filter(**params.dict())
        return qs

