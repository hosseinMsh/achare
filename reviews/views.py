from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db.models import Avg, Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from ads.models import Advertisement
from .models import Review
from .serializers import CreateReviewSerializer, ReviewSerializer

User = get_user_model()


class ReviewCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateReviewSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.create(serializer.validated_data)
        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


class ContractorReviewsView(generics.ListAPIView):
    """List reviews for a contractor.

    Optional part: filter by rating using ?rating=1..5
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        contractor_id = self.kwargs['contractor_id']
        qs = Review.objects.filter(contractor_id=contractor_id).order_by('-created_at')
        rating = self.request.query_params.get('rating')
        if rating:
            try:
                r = int(rating)
                qs = qs.filter(rating=r)
            except ValueError:
                pass
        return qs


class ContractorListView(APIView):
    """List contractors with filtering/sorting.

    Query params:
    - min_rating: float
    - min_reviews: int
    - ordering: 'rating' | '-rating' | 'review_count' | '-review_count'
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        min_rating = request.query_params.get('min_rating')
        min_reviews = request.query_params.get('min_reviews')
        ordering = request.query_params.get('ordering')

        qs = User.objects.filter(roles__name='contractor').distinct()
        qs = qs.annotate(
            review_count=Count('reviews_received', distinct=True),
            avg_rating=Avg('reviews_received__rating'),
            done_ads=Count('assigned_ads', filter=Q(assigned_ads__status=Advertisement.STATUS_DONE), distinct=True),
        )

        if min_rating is not None:
            try:
                qs = qs.filter(avg_rating__gte=float(min_rating))
            except ValueError:
                pass

        if min_reviews is not None:
            try:
                qs = qs.filter(review_count__gte=int(min_reviews))
            except ValueError:
                pass

        if ordering in {'rating', '-rating'}:
            qs = qs.order_by(('-' if ordering.startswith('-') else '') + 'avg_rating')
        elif ordering in {'review_count', '-review_count'}:
            qs = qs.order_by(('-' if ordering.startswith('-') else '') + 'review_count')
        else:
            qs = qs.order_by('-avg_rating', '-review_count')

        data = []
        for u in qs:
            data.append({
                'id': u.id,
                'username': u.username,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'done_ads': u.done_ads,
                'avg_rating': u.avg_rating or 0,
                'review_count': u.review_count,
            })
        return Response(data)


class ContractorProfileView(APIView):
    """Contractor profile + stats + latest reviews."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, contractor_id: int):
        contractor = generics.get_object_or_404(User, id=contractor_id, roles__name='contractor')

        stats = Review.objects.filter(contractor_id=contractor_id).aggregate(
            avg_rating=Avg('rating'),
            review_count=Count('id')
        )
        done_ads = Advertisement.objects.filter(contractor_id=contractor_id, status=Advertisement.STATUS_DONE).count()
        reviews_qs = Review.objects.filter(contractor_id=contractor_id).order_by('-created_at')

        return Response({
            'contractor': {
                'id': contractor.id,
                'username': contractor.username,
                'first_name': contractor.first_name,
                'last_name': contractor.last_name,
            },
            'done_ads': done_ads,
            'avg_rating': stats['avg_rating'] or 0,
            'review_count': stats['review_count'],
            'reviews': ReviewSerializer(reviews_qs, many=True).data,
        })


class CustomerProfileView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, customer_id: int):
        customer = generics.get_object_or_404(User, id=customer_id)
        ads = Advertisement.objects.filter(customer_id=customer_id).order_by('-created_at')
        return Response({
            'customer': {
                'id': customer.id,
                'username': customer.username,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
            },
            'ads': [
                {
                    'id': a.id,
                    'title': a.title,
                    'status': a.status,
                    'created_at': a.created_at,
                } for a in ads
            ]
        })
