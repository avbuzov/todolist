from django.db import models
from django.utils import timezone

from core.models import User
from todolist.models import DatesModel


class GoalCategory(DatesModel):
    title = models.CharField(verbose_name="Название", max_length=255)
    user = models.ForeignKey(User, verbose_name="Автор", on_delete=models.PROTECT)
    is_deleted = models.BooleanField(verbose_name="Удалена", default=False)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Goal(DatesModel):
    class Status(models.IntegerChoices):
        to_do = 1, "К выполнению"
        in_progress = 2, "В процессе"
        done = 3, "Выполнено"
        archived = 4, "Архив"

    class Priority(models.IntegerChoices):
        low = 1, "Низкий"
        medium = 2, "Средний"
        high = 3, "Высокий"
        critical = 4, "Критический"

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(GoalCategory, on_delete=models.PROTECT)
    due_date = models.DateField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(verbose_name="Статус", choices=Status.choices, default=Status.to_do)
    priority = models.PositiveSmallIntegerField(verbose_name="Приоритет", choices=Priority.choices, default=Priority.medium)

    class Meta:
        verbose_name = "Цель"
        verbose_name_plural = "Цели"


class GoalComment(DatesModel):
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    goal = models.ForeignKey(Goal, on_delete=models.PROTECT)
    text = models.TextField()

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"


    # def save(self, *args, **kwargs):
    #     if not self.id:  # Когда объект только создается, у него еще нет id
    #         self.created = timezone.now()  # проставляем дату создания
    #     self.updated = timezone.now()  # проставляем дату обновления
    #     return super().save(*args, **kwargs)
