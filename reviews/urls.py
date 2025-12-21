from django.urls import path

from .views import (
    ContractorListView,
    ContractorProfileView,
    ContractorReviewsView,
    CustomerProfileView,
    ReviewCreateView,
)

urlpatterns = [
    path('reviews/', ReviewCreateView.as_view(), name='create-review'),
    path('contractors/', ContractorListView.as_view(), name='contractor-list'),
    path('contractors/<int:contractor_id>/profile/', ContractorProfileView.as_view(), name='contractor-profile'),
    path('contractors/<int:contractor_id>/reviews/', ContractorReviewsView.as_view(), name='contractor-reviews'),
    path('customers/<int:customer_id>/profile/', CustomerProfileView.as_view(), name='customer-profile'),
]
