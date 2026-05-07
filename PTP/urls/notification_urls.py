from django.urls import path
from PTP.views import (
    NotificationListView,
    MarkNotificationReadView,
    AdminSendNotificationView,
)
from django.urls import path
from PTP.views.expo_push_token_views import SaveExpoPushTokenView
 
urlpatterns = [
    # POST /api/expo/token/
    # Called after every login to upsert the Expo push token.
    path('expo/token', SaveExpoPushTokenView.as_view(), name='save-expo-push-token'),
]
 