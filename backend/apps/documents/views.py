from rest_framework import generics, permissions
from .models import JobDescription, ReferenceResume
from .serializers import JobDescriptionSerializer, ReferenceResumeSerializer

class JobDescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = JobDescriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class JobDescriptionDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = JobDescriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return JobDescription.objects.filter(user=self.request.user)


class ReferenceResumeListCreateView(generics.ListCreateAPIView):
    serializer_class = ReferenceResumeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ReferenceResume.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReferenceResumeDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = ReferenceResumeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return ReferenceResume.objects.filter(user=self.request.user)
