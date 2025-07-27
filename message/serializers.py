from rest_framework import serializers
from api.responses import *
from user.models import Role, User
from .models import AlarmMessage, Department, SmsMessage, WebMessage, WebMessageContent, MessageStatus, MessageType
from api.mixins import CustomModelSerializer, CustomChoiceField


class DepartmentSerializer(CustomModelSerializer):
    """
    MEH: Department full Information
    """
    employees_display = serializers.StringRelatedField(source='employees', read_only=True, many=True)

    class Meta:
        model = Department
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('view').action == 'list': # MEH: drop employee-list in list view
            data.pop('employees_display', None)
            data.pop('employees', None)
        return data


class SmsMessageSerializer(CustomModelSerializer):
    """
    MEH: Sms Message history full Information
    """
    receiver = serializers.StringRelatedField()

    class Meta:
        model = SmsMessage
        fields = '__all__'


class WebMessageContentSerializer(CustomModelSerializer):
    """
    MEH: Web Message content full Information
    """
    class Meta:
        model = WebMessageContent
        fields = '__all__'
        read_only_fields = ['id', 'parent', 'type']

    def create(self, validated_data):
        status_data = validated_data.pop('status', None)
        msg = super().create(validated_data)
        if msg and status_data:
            parent = msg.parent
            parent.status=status_data
            parent.save()
        return msg


class WebMessageSerializer(CustomModelSerializer):
    """
    MEH: Web Message full Information
    """
    user_display = serializers.StringRelatedField(source='user', read_only=True)
    employee = serializers.StringRelatedField(read_only=True)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    department_display = serializers.StringRelatedField(source='department', read_only=True)

    class Meta:
        model = WebMessage
        fields = '__all__'
        read_only_fields = ['id', 'status']


class WebMessageFileAccessSerializer(CustomModelSerializer):
    """
    MEH: Web Message file access Information
    """
    class Meta:
        model = WebMessage
        fields = ['id', 'file_access']


class WebMessageWithContentSerializer(WebMessageSerializer):
    """
    MEH: Web Message full Information with nested content data
    """
    content_list = WebMessageContentSerializer(many=True, read_only=True)


class WebMessageRequestNewSerializer(WebMessageSerializer):
    """
    MEH: Web Message New message request Information
    """
    content = WebMessageContentSerializer()

    class Meta:
        model = WebMessage
        exclude = ['file_access', 'status']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        content_data = validated_data.pop('content', {})
        file = content_data.pop('file', None)
        if file:
            raise serializers.ValidationError(TG_DATA_WRONG)
        if content_data:
            web_message = WebMessage.objects.create(**validated_data)
            WebMessageContent.objects.create(**content_data, parent=web_message)
            return web_message
        raise serializers.ValidationError(TG_DATA_EMPTY)


class WebMessageSendNewSerializer(WebMessageSerializer):
    """
    MEH: Web Message send new message Information
    """
    content = WebMessageContentSerializer()

    class Meta:
        model = WebMessage
        exclude = ['type', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee_profile'):  # MEH: Make sure only available department set
            employee = request.user.employee_profile
            self.fields['department'].queryset = Department.objects.filter(employees=employee)

    def create(self, validated_data):
        content_data = validated_data.pop('content', {})
        if content_data:
            web_message = WebMessage.objects.create(**validated_data, status=MessageStatus.ADMIN)
            WebMessageContent.objects.create(**content_data, parent=web_message, type=MessageType.SEND)
            return web_message
        raise serializers.ValidationError(TG_DATA_EMPTY)


class WebMessageContentEmployeeResponseSerializer(WebMessageContentSerializer):
    """
    MEH: Web Message content Employee Response information
    """
    status = CustomChoiceField(choices=MessageStatus.choices, required=True)


class WebMessageContentUserResponseSerializer(WebMessageContentSerializer):
    """
    MEH: Web Message content User Response information
    """
    def create(self, validated_data):
        parent = validated_data.get('parent')
        if parent.status == MessageStatus.PENDING:
            raise serializers.ValidationError(TG_WAIT_FOR_RESPONSE)
        if parent.status == MessageStatus.ENDED:
            raise serializers.ValidationError(TG_MESSAGE_CLOSED)
        if validated_data.get('file'): # MEH: This mean user send file so most check permission!
            if parent and parent.access_file:
                return super().create(validated_data)
            raise serializers.ValidationError(TG_DONT_ALLOW_FILE)
        return super().create(validated_data)


class WebMessageGroupSendingSerializer(serializers.Serializer):
    """
    MEH: Web Message group sending Information
    """
    title = serializers.CharField(max_length=78)
    content = serializers.CharField(max_length=500)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False)
    users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all().filter(is_employee=False), required=False, many=True)
    role = serializers.PrimaryKeyRelatedField(queryset=Role.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee_profile'):  # MEH: Make sure only available department set
            employee = request.user.employee_profile
            self.fields['department'].queryset = Department.objects.filter(employees=employee)

    def validate(self, data):
        if not any([data.get("user_ids"), data.get("role")]):
            raise serializers.ValidationError("At least one of 'user_ids' or 'role' is required.")
        return data


class AlarmMessageSerializer(CustomModelSerializer):
    """
    MEH: Alarm Message full Information
    """
    employee = serializers.StringRelatedField(read_only=True)
    roles_display = serializers.StringRelatedField(source='roles', read_only=True, many=True)

    class Meta:
        model = AlarmMessage
        fields = '__all__'
