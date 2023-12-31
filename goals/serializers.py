from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from core.models import User
from core.serializers import ProfileSerializer
from goals.models import GoalCategory, Goal, GoalComment, Board, BoardParticipant


class BoardSerializer(serializers.ModelSerializer):
    """
    Сериализатор для доски
    """
    class Meta:
        model = Board
        read_only_fields = ('id', 'created', 'updated', 'is_deleted')
        fields = '__all__'


class ParticipantSerializer(serializers.ModelSerializer):
    """
    Сериализатор для участника
    """
    role = serializers.ChoiceField(choices=BoardParticipant.editable_roles)
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())

    class Meta:
        model = BoardParticipant
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'board')


class BoardWithParticipantsSerializer(BoardSerializer):
    """
    Сериализатор для доски c участником
    """
    participants = ParticipantSerializer(many=True)

    def update(self, instance: Board, validated_data: dict) -> Board:
        owner = validated_data.pop("user")
        new_participants = validated_data.pop("participants")
        new_by_id = {part["user"].id: part for part in new_participants}

        old_participants = instance.participants.exclude(user=owner)
        with transaction.atomic():
            for old_participant in old_participants:
                if old_participant.user_id not in new_by_id:
                    old_participant.delete()
                else:
                    if (
                            old_participant.role != new_by_id[old_participant.user_id]["role"]
                    ):
                        old_participant.role = new_by_id[old_participant.user_id]["role"]
                        old_participant.save()
                    new_by_id.pop(old_participant.user_id)
            for new_part in new_by_id.values():
                BoardParticipant.objects.create(
                    board=instance, user=new_part["user"], role=new_part["role"]
                )

            instance.title = validated_data["title"]
            instance.save()

        return instance


class GoalCategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для категории с целью
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    def validate_board(self, board: Board) -> Board:
        if board.is_deleted:
            raise ValidationError('Board not exists')
        if not BoardParticipant.objects.filter(
            board_id=board.id,
            user_id=self.context['request'].user.id,
            role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise PermissionDenied('Permission denied')
        return board

    class Meta:
        model = GoalCategory
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user', 'is_deleted')


class GoalCategoryWithUserSerializer(GoalCategorySerializer):
    """
    Сериализатор для категории и цели по пользователю
    """
    user = ProfileSerializer(read_only=True)


class GoalSerializer(serializers.ModelSerializer):
    """
    Сериализатор для цели
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Goal
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_category(self, category: GoalCategory) -> GoalCategory:
        if category.is_deleted:
            raise ValidationError('Category not exists')
        if not BoardParticipant.objects.filter(
                board_id=category.board_id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise PermissionDenied('Permission denied')
        return category


class GoalWithUserSerializer(GoalSerializer):
    """
    Сериализатор для цели с пользователем
    """
    user = ProfileSerializer(read_only=True)


class GoalCommentSerializer(serializers.ModelSerializer):
    """
    Сериализатор для комментария и цели
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = GoalComment
        fields = '__all__'
        read_only_fields = ('id', 'created', 'updated', 'user')

    def validate_goal(self, goal: Goal) -> Goal:
        if goal.status == Goal.Status.archived:
            raise ValidationError('Goal not exists')
        if not BoardParticipant.objects.filter(
                board_id=goal.category.board_id,
                user_id=self.context['request'].user.id,
                role__in=[BoardParticipant.Role.owner, BoardParticipant.Role.writer]
        ).exists():
            raise PermissionDenied('Permission denied')
        return goal


class GoalCommentWithUserSerializer(GoalCommentSerializer):
    """
    Сериализатор для комментария и цели с привязкой к пользователю
    """
    user = ProfileSerializer(read_only=True)
    goals = serializers.PrimaryKeyRelatedField(read_only=True)
