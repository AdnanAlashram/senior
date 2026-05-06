from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from PTP.models.expo_push_token import ExpoPushToken


class SaveExpoPushTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # نحفظ أو نحدّث التوكن
        obj, created = ExpoPushToken.objects.update_or_create(
            user=user,
            defaults={"token": token}
        )

        return Response({
            "message": "Token saved successfully",
            "created": created
        }, status=status.HTTP_200_OK)