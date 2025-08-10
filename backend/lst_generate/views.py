# lst_generate/views.py
from rest_framework import viewsets, permissions
from .models import Listing
from .serializers import ListingDetailSerializer

class ListingViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ListingDetailSerializer
    permission_classes = [permissions.IsAuthenticated] # 只有提供了有效 JWT Token 的已登录用户才能通过

    def get_queryset(self):
        """
        核心：确保用户只能看到自己的数据。
        """
        user = self.request.user
        return Listing.objects.filter(user=user)