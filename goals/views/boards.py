from django.db import transaction
from django.db.models import QuerySet
from rest_framework import generics, permissions, filters

from goals.models import BoardParticipant, Board, Goal
from goals.permissions import BoardPermission
from goals.serializers import BoardSerializer, BoardWithParticipantsSerializer


class BoardCreateView(generics.CreateAPIView):
    """
    Создание доски
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer

    def perform_create(self, serializer) -> None:
        with transaction.atomic():
            board = serializer.save()
            BoardParticipant.objects.create(user=self.request.user, board=board)


class BoardListView(generics.ListAPIView):
    """
    Вывод списка досок
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BoardSerializer
    filter_backends = [filters.OrderingFilter]
    ordering = ['title']

    def get_queryset(self) -> QuerySet[Board]:
        return Board.objects.filter(participants__user=self.request.user).exclude(is_deleted=True)


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Вывод одной доски
    """
    permission_classes = [BoardPermission]
    serializer_class = BoardWithParticipantsSerializer

    def get_queryset(self) -> QuerySet[Board]:
        return Board.objects.prefetch_related('participants__user').exclude(is_deleted=True)

    def perform_destroy(self, instance: Board) -> None:
        with transaction.atomic():
            instance.is_deleted = True
            instance.save()
            instance.categories.update(is_deleted=True)
            Goal.objects.filter(category__board=instance).update(status=Goal.Status.archived)
