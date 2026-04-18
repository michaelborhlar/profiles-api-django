from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from uuid_extensions import uuid7str

from .models import Profile
from .serializers import ProfileDetailSerializer, ProfileListSerializer
from .services import (
    fetch_genderize, fetch_agify, fetch_nationalize,
    classify_age, ExternalAPIError,
)


class ProfileListCreateView(APIView):

    def post(self, request):
        name = request.data.get('name')

        # Validation
        if name is None or name == '':
            return Response(
                {'status': 'error', 'message': 'Missing or empty name'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(name, str):
            return Response(
                {'status': 'error', 'message': 'Invalid type'},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        normalized = name.strip().lower()

        # Idempotency check
        try:
            existing = Profile.objects.get(name=normalized)
            serializer = ProfileDetailSerializer(existing)
            return Response(
                {
                    'status': 'success',
                    'message': 'Profile already exists',
                    'data': serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Profile.DoesNotExist:
            pass

        # Call external APIs
        try:
            gender_data = fetch_genderize(normalized)
        except ExternalAPIError as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            age_data = fetch_agify(normalized)
        except ExternalAPIError as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        try:
            country_data = fetch_nationalize(normalized)
        except ExternalAPIError as e:
            return Response(
                {'status': 'error', 'message': str(e)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        profile = Profile.objects.create(
            id=uuid7str(),
            name=normalized,
            gender=gender_data['gender'],
            gender_probability=gender_data['gender_probability'],
            sample_size=gender_data['sample_size'],
            age=age_data['age'],
            age_group=classify_age(age_data['age']),
            country_id=country_data['country_id'],
            country_probability=country_data['country_probability'],
            created_at=timezone.now(),
        )

        serializer = ProfileDetailSerializer(profile)
        return Response(
            {'status': 'success', 'data': serializer.data},
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        queryset = Profile.objects.all()

        gender = request.query_params.get('gender')
        country_id = request.query_params.get('country_id')
        age_group = request.query_params.get('age_group')

        if gender:
            queryset = queryset.filter(gender__iexact=gender)
        if country_id:
            queryset = queryset.filter(country_id__iexact=country_id)
        if age_group:
            queryset = queryset.filter(age_group__iexact=age_group)

        serializer = ProfileListSerializer(queryset, many=True)
        return Response(
            {
                'status': 'success',
                'count': queryset.count(),
                'data': serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class ProfileDetailView(APIView):

    def get(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ProfileDetailSerializer(profile)
        return Response({'status': 'success', 'data': serializer.data})

    def delete(self, request, pk):
        try:
            profile = Profile.objects.get(pk=pk)
        except Profile.DoesNotExist:
            return Response(
                {'status': 'error', 'message': 'Profile not found'},
                status=status.HTTP_404_NOT_FOUND,
            )
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
