from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CareerProfile, Experience, Project, Skill, Education, Certification
from .serializers import (
    CareerProfileSerializer,
    ExperienceSerializer,
    ProjectSerializer,
    SkillSerializer,
    EducationSerializer,
    CertificationSerializer,
)

def get_or_create_user_profile(user):
    profile, _ = CareerProfile.objects.get_or_create(
        user=user,
        defaults={
            'full_name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'email': user.email or '',
        }
    )
    return profile


class CareerProfileView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        profile = get_or_create_user_profile(request.user)
        serializer = CareerProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = get_or_create_user_profile(request.user)
        serializer = CareerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Experience.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_or_create_user_profile(self.request.user)
        serializer.save(profile=profile)


class ExperienceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Experience.objects.filter(profile=profile)


class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Project.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_or_create_user_profile(self.request.user)
        serializer.save(profile=profile)


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Project.objects.filter(profile=profile)


class SkillListCreateView(generics.ListCreateAPIView):
    serializer_class = SkillSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Skill.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_or_create_user_profile(self.request.user)
        # Handle update if same name and category exist
        name = serializer.validated_data.get('name')
        category = serializer.validated_data.get('category')
        existing = Skill.objects.filter(profile=profile, name__iexact=name, category=category).first()
        if existing:
            existing.proficiency_level = serializer.validated_data.get('proficiency_level', existing.proficiency_level)
            existing.years_used = serializer.validated_data.get('years_used', existing.years_used)
            existing.save()
            return existing
        serializer.save(profile=profile)


class SkillDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = SkillSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Skill.objects.filter(profile=profile)


class EducationListCreateView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Education.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_or_create_user_profile(self.request.user)
        serializer.save(profile=profile)


class EducationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EducationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Education.objects.filter(profile=profile)


class CertificationListCreateView(generics.ListCreateAPIView):
    serializer_class = CertificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Certification.objects.filter(profile=profile)

    def perform_create(self, serializer):
        profile = get_or_create_user_profile(self.request.user)
        serializer.save(profile=profile)


class CertificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CertificationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        profile = get_or_create_user_profile(self.request.user)
        return Certification.objects.filter(profile=profile)
