from rest_framework import viewsets, permissions, status, generics
from .serializers import (UserSerializer)
from .models import ( User)
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.serializers import AuthTokenSerializer
from knox.auth import AuthToken
from datetime import datetime
from django.shortcuts import render
from .models import Location, Board, Register, Notification, HistoricalData, HistoricalControl, RegisterSetting, MaintenanceRecord, Tag
from .serializers import (
    LocationReadSerializer, LocationWriteSerializer,
    BoardReadSerializer, BoardWriteSerializer, 
    RegisterReadSerializer, RegisterWriteSerializer, 
    NotificationReadSerializer, NotificationWriteSerializer, 
    HistoricalDataReadSerializer, HistoricalDataWriteSerializer, 
    HistoricalControlReadSerializer, HistoricalControlWriteSerializer, 
    RegisterSettingReadSerializer, RegisterSettingWriteSerializer, 
    MaintenanceRecordReadSerializer, MaintenanceRecordWriteSerializer,
    TagSerializer
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from .paginator import StandardResultsSetPagination

@api_view(['POST'])
def login_api(request):
    permission_classes = [permissions.AllowAny]
    serializer = AuthTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']

    user.auth_token_set.all().delete()
    _, token = AuthToken.objects.create(user)

    device_token = request.data.get('device_token')
    if device_token is not None:
        user.device_token = device_token
        user.save()

    return Response({
        'user_info': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'device_token': user.device_token,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'name': user.name,
            'is_superuser': user.is_superuser,
        },
        'token': token
    })


@api_view(['GET'])
def get_user_data(request):
    user = request.user

    if user is not None:
        return Response(data={'user_info': {
            'id': user.id,
            'username': user.username,
            'email': user.email
        }})
    return Response(data={'error': 'not authenticated'}, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ViewSet, generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView, generics.RetrieveAPIView, generics.DestroyAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(methods=['get'], detail=False, url_path='current-user')
    def get_current_user(seft, request):
        return Response(seft.serializer_class(request.user).data, status=status.HTTP_200_OK)

    def list(self, request):
        users = User.objects.filter(is_active=True)
        building = request.query_params.get('building')
        if building is not None:
            users = users.filter(building=building)

        serializer = UserSerializer(users, many=True)
        return Response(data={"users": serializer.data}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def boards(self, request, pk=None):
        user = self.get_object()
        paginator = StandardResultsSetPagination()
        if user.is_superuser:
            boards = Board.objects.all()
        else:
            boards = user.accessible_boards.all()
        result_page = paginator.paginate_queryset(boards, request)
        serializer = BoardReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        user = self.get_object()
        paginator = StandardResultsSetPagination()
        if user.is_superuser:
            locations = Location.objects.all()
        else:
            locations = user.accessible_locations.all()
        result_page = paginator.paginate_queryset(locations, request)
        serializer = LocationReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def destroy(self, request, pk, *args, **kwargs):
        user = User.objects.get(pk=pk)
        user.is_active = False
        user.save()
        return Response(status=204)
    
class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LocationReadSerializer
        return LocationWriteSerializer
    
    @action(detail=True, methods=['get']) 
    def boards(self, request, pk=None): 
        location = self.get_object() 
        paginator = StandardResultsSetPagination()
        boards = location.boards.all() 
        result_page = paginator.paginate_queryset(boards, request)
        serializer = BoardReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return BoardReadSerializer
        return BoardWriteSerializer
    
    @action(detail=True, methods=['get']) 
    def registers(self, request, pk=None): 
        board = self.get_object() 
        paginator = StandardResultsSetPagination()
        registers = board.registers.all()
        result_page = paginator.paginate_queryset(registers, request)
        serializer = RegisterReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get']) 
    def notifications(self, request, pk=None): 
        board = self.get_object() 
        paginator = StandardResultsSetPagination()
        notifications = board.notifications.all()
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get']) 
    def maintenance_records(self, request, pk=None): 
        board = self.get_object() 
        paginator = StandardResultsSetPagination()
        maintenance_records = board.maintenance_records.all() 
        result_page = paginator.paginate_queryset(maintenance_records, request)
        serializer = MaintenanceRecordReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Register.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RegisterReadSerializer
        return RegisterWriteSerializer
    
    @action(detail=True, methods=['get']) 
    def historical_data(self, request, pk=None): 
        register = self.get_object() 
        paginator = StandardResultsSetPagination()
        historical_data = register.historical_data.all()
        result_page = paginator.paginate_queryset(historical_data, request)
        serializer = HistoricalDataReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get']) 
    def historical_controls(self, request, pk=None): 
        register = self.get_object() 
        paginator = StandardResultsSetPagination()
        historical_controls = register.historical_controls.all()
        result_page = paginator.paginate_queryset(historical_controls, request)
        serializer = HistoricalControlReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get']) 
    def register_settings(self, request, pk=None): 
        register = self.get_object() 
        paginator = StandardResultsSetPagination()
        settings = register.register_settings.all()
        result_page = paginator.paginate_queryset(settings, request)
        serializer = RegisterSettingReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get']) 
    def maintenance_records(self, request, pk=None): 
        register = self.get_object() 
        paginator = StandardResultsSetPagination()
        maintenance_records = register.maintenance_records.all()
        result_page = paginator.paginate_queryset(maintenance_records, request)
        serializer = MaintenanceRecordReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get']) 
    def notifications(self, request, pk=None): 
        register = self.get_object() 
        paginator = StandardResultsSetPagination()
        notifications = register.notifications.all()
        result_page = paginator.paginate_queryset(notifications, request)
        serializer = NotificationReadSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return NotificationReadSerializer
        return NotificationWriteSerializer

class HistoricalDataViewSet(viewsets.ModelViewSet):
    queryset = HistoricalData.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return HistoricalDataReadSerializer
        return HistoricalDataWriteSerializer

class HistoricalControlViewSet(viewsets.ModelViewSet):
    queryset = HistoricalControl.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return HistoricalControlReadSerializer
        return HistoricalControlWriteSerializer

class RegisterSettingViewSet(viewsets.ModelViewSet):
    queryset = RegisterSetting.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RegisterSettingReadSerializer
        return RegisterSettingWriteSerializer

class MaintenanceRecordViewSet(viewsets.ModelViewSet):
    queryset = MaintenanceRecord.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return MaintenanceRecordReadSerializer
        return MaintenanceRecordWriteSerializer

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer

    @action(detail=False, methods=['get'])
    def search_by_code(self, request):
        tag_code = request.query_params.get('tag_code', None)
        if tag_code:
            tags = Tag.objects.filter(tag_code=tag_code)
            if tags.exists():
                serializer = TagSerializer(tags, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'No tags found with this code.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'detail': 'Tag code parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['POST'])
def receive_data(request):
    data = request.data
    print('Received data:', data)
    board_id = data.get('id')
    print('Board ID:', board_id)
    
    try:
        board = Board.objects.get(device_id=board_id)
        print('Board found:', board)
    except Board.DoesNotExist:
        print('Board not found')
        return Response({'status': 'fail', 'message': 'Board not found'}, status=404)
    
    data_list = data.get('data', [])
    print('Data list:', data_list)
    
    for item in data_list:
        print('Processing item:', item)
        name = item.get('name')
        
        for key, value in item.items():
            if key.startswith('value'):
                obj, created = Register.objects.update_or_create(
                    board=board,
                    name=name,
                    defaults={'value': value}
                )

                if not created:
                    HistoricalData.objects.create(
                        register=obj,
                        type=obj.type,
                        value=value
                    )
                print('Register object:', obj, 'Created:', created)
    
    return Response({'status': 'success'}, status=201)



@api_view(['POST'])
def notification_data(request):
    data = request.data
    print('Notification data:', data)
    board_id = data.get('id')
    print('Board ID:', board_id)
    
    try:
        board = Board.objects.get(device_id=board_id)
        print('Board found:', board)
    except Board.DoesNotExist:
        print('Board not found')
        return Response({'status': 'fail', 'message': 'Board not found'}, status=404)
    
    data = data.get('data')
    Notification.objects.create(
        board=board,
        # register=register,
        title=data['title'],
        description=data['description']
    )
     
    return Response({'status': 'success'}, status=201)


@api_view(['POST'])
def setting_data(request):
    data = request.data
    print('Setting data:', data)
    board_id = data.get('id')
    print('Board ID:', board_id)
    
    try:
        board = Board.objects.get(device_id=board_id)
        print('Board found:', board)
    except Board.DoesNotExist:
        print('Board not found')
        return Response({'status': 'fail', 'message': 'Board not found'}, status=404)
    
    data_list = data.get('data', [])
    if not data_list:
        return Response({'status': 'fail', 'message': 'Data not provided'}, status=400)

    for item in data_list:
        try:
            register = Register.objects.get(name=item['name'], board=board)
            print('Register found:', register)
        except Register.DoesNotExist:
            print('Register not found')
            continue
        
        RegisterSetting.objects.create(
            board=board,
            register=register,
            type=item['type'],
            value=item['value'],
        )
    
    return Response({'status': 'success'}, status=201)


