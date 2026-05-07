from django.db import transaction
from django.contrib.auth.hashers import make_password
 
from PTP.models import Driver, Route, Vehicle
from PTP.models.user import User
from PTP.services.expo_token_service import ExpoTokenService
 
 
class AccountService:
 
    @transaction.atomic
    def register_user(
        self,
        email,
        full_name,
        phone,
        password,
        account_type,
        id_card_image_1=None,
        id_card_image_2=None,
        license_image=None,
        has_vehicle=False,
        vehicle_type=None,
        vehicle_number=None,
        route_id=None,
        expo_push_token=None,
    ):
        if account_type == 'driver':
            vehicle = None
            if has_vehicle:
                route = None
                if route_id:
                    route = Route.objects.filter(route_id=route_id).first()
 
                vehicle = Vehicle.objects.create(
                    vehicle_type=vehicle_type,
                    vehicle_number=vehicle_number,
                    ownership='driver',
                    route=route,
                )
 
            driver = Driver.objects.create(
                full_name=full_name,
                email=email,
                phone=phone,
                password=make_password(password),
                id_card_image_1=id_card_image_1,
                id_card_image_2=id_card_image_2,
                license_image=license_image,
                vehicle=vehicle,
                # expo_push_token field on Driver model is now unused —
                # token is stored in the unified ExpoPushToken table below
            )
 
            # Save token to unified table (driver_id is now known, never NULL)
            if expo_push_token:
                ExpoTokenService.upsert_driver_token(
                    driver_id=driver.driver_id,
                    token=expo_push_token,
                )
 
            return driver
 
        # ── Passenger ────────────────────────────────────────────────────────
        user = User.objects.create_user(
            email=email,
            full_name=full_name,
            phone=phone,
            password=password,
            is_admin=False,
        )
 
        # Save token to unified table (user_id is now known, never NULL)
        if expo_push_token:
            ExpoTokenService.upsert_passenger_token(
                user_id=user.id,
                token=expo_push_token,
            )
 
        return user