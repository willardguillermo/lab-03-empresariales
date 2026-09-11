from django.core.management.base import BaseCommand
from django.db import transaction

from quiz.models import Choice, Exam, Question


class Command(BaseCommand):
    """Seeds the database with a sample Exam, Questions and Choices.

    This command speeds up manual testing and grading; it does not
    replace the admin data entered by hand in a previous step.
    Running it more than once is safe: the Exam is looked up by
    title, and if it already exists its questions (and, through the
    CASCADE foreign key, their choices) are deleted and recreated
    instead of duplicated.
    """

    help = 'Seeds the database with a sample exam, questions and choices.'

    EXAM_TITLE = 'Django Fundamentals Quiz'
    EXAM_DESCRIPTION = (
        'Sample exam covering basic Django concepts, used to seed '
        'test data for the quiz app.'
    )

    # Each entry is (question text, list of 4 choice texts, index of
    # the correct choice within that list).
    QUESTIONS = [
        (
            'What does MVC stand for in the context of web '
            'frameworks?',
            [
                'Model-View-Controller',
                'Model-Variable-Component',
                'Multiple-View-Control',
                'Module-View-Class',
            ],
            0,
        ),
        (
            'Which command creates a new Django project?',
            [
                'django-admin startproject',
                'django-admin startapp',
                'python manage.py newproject',
                'django-admin createproject',
            ],
            0,
        ),
        (
            'What is the default database engine for a new Django '
            'project?',
            ['PostgreSQL', 'MySQL', 'SQLite', 'Oracle'],
            2,
        ),
        (
            "Which file defines a Django app's data models?",
            ['views.py', 'models.py', 'urls.py', 'admin.py'],
            1,
        ),
        (
            'Which ORM method retrieves every row of a model?',
            [
                'Model.objects.all()',
                'Model.objects.get()',
                'Model.objects.filter(None)',
                'Model.all()',
            ],
            0,
        ),
        (
            'Which command applies pending database migrations?',
            [
                'python manage.py makemigrations',
                'python manage.py migrate',
                'python manage.py runserver',
                'python manage.py syncdb',
            ],
            1,
        ),
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        exam, created = Exam.objects.get_or_create(
            title=self.EXAM_TITLE,
            defaults={'description': self.EXAM_DESCRIPTION},
        )

        if not created:
            # Re-seed from scratch: deleting the exam's questions also
            # deletes their choices, thanks to on_delete=CASCADE.
            exam.questions.all().delete()

        question_count = 0
        choice_count = 0

        for question_text, choice_texts, correct_index in self.QUESTIONS:
            question = Question.objects.create(
                text=question_text,
                exam=exam,
            )
            question_count += 1

            for index, choice_text in enumerate(choice_texts):
                Choice.objects.create(
                    text=choice_text,
                    question=question,
                    is_correct=(index == correct_index),
                )
                choice_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Exam "{exam.title}" (id={exam.pk}): '
            f'{question_count} questions, '
            f'{choice_count} choices created.'
        ))
