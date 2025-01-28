from rest_framework import response, status, viewsets

try:
    from rest_framework.decorators import action

    action_params = {"detail": False}
except ImportError:
    from rest_framework.decorators import list_route as action

    action_params = {}

from rest_framework.response import Response

from whisperer.events import registry
from whisperer.exceptions import WebhookAlreadyRegistered
from whisperer.models import EventQueue, Webhook, WebhookEvent
from whisperer.resources.filters import (
    EventQueueFilter,
    WebhookEventFilter,
    WebhookFilter,
)
from whisperer.resources.serializers import (
    EventQueueSerializer,
    WebhookEventSerializer,
    WebhookSerializer,
)
from whisperer.services import WebhookService


class WebhookViewSet(viewsets.ModelViewSet):
    queryset = Webhook.objects.all()
    serializer_class = WebhookSerializer
    service = WebhookService()
    filter_class = WebhookFilter
    filterset_class = WebhookFilter

    def get_queryset(self):
        queryset = super(WebhookViewSet, self).get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            self.perform_create(serializer)
        except WebhookAlreadyRegistered as exception:
            return response.Response(
                data=exception.code, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        user = self.request.user
        serializer.instance = self.service.register_webhook(
            user, **serializer.validated_data
        )

    def perform_update(self, serializer):
        user = self.request.user
        self.service.update_webhook(
            serializer.instance, user=user, **serializer.validated_data
        )

    def perform_destroy(self, instance):
        self.service.delete_webhook(instance)

    @action(methods=["GET"], url_path="registry", **action_params)
    def get_registry(self, *args, **kwargs):
        registry_keys = list(registry.keys())
        return Response(registry_keys, status=status.HTTP_200_OK)


class WebhookEventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = WebhookEvent.objects.all()
    filter_class = WebhookEventFilter
    filterset_class = WebhookEventFilter
    serializer_class = WebhookEventSerializer

    def get_queryset(self):
        queryset = super(WebhookEventViewSet, self).get_queryset()
        if self.request.user.is_superuser:
            return queryset
        return queryset.filter(webhook__user=self.request.user)


class EventQueueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventQueue.objects.all()
    filter_class = EventQueueFilter
    filterset_class = EventQueueFilter
    serializer_class = EventQueueSerializer
