from django.db import models


class Exam(models.Model):
    """Represents an exam that groups multiple questions."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Examen'
        verbose_name_plural = 'Exámenes'

    def __str__(self):
        return self.title


class Question(models.Model):
    """Represents a single question that belongs to an exam."""

    SUMMARY_LENGTH = 50

    text = models.TextField()
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Pregunta'
        verbose_name_plural = 'Preguntas'

    def __str__(self):
        if len(self.text) > self.SUMMARY_LENGTH:
            return f'{self.text[:self.SUMMARY_LENGTH]}...'
        return self.text


class Choice(models.Model):
    """Represents a possible answer option for a question."""

    text = models.CharField(max_length=200)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
    )
    is_correct = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']
        verbose_name = 'Opción'
        verbose_name_plural = 'Opciones'

    def __str__(self):
        return self.text
