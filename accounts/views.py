import structlog
from drf_yasg.utils import swagger_auto_schema
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.serializers import UserSerializer

logger = structlog.get_logger(__name__)

AUTH_HEADER_KEY = "Authorization"


class UserAPIView(APIView):
    @swagger_auto_schema(responses={200: UserSerializer})
    def get(self, request):
        """Get user information."""
        user = User.objects.get(pk=request.user.pk)
        serialized_user = UserSerializer(user).data
        return Response({"user": serialized_user})


class AccountAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        if not request.user.is_superuser:  # type: ignore
            raise PermissionDenied("Not superuser")
        return super().list(request, *args, **kwargs)
