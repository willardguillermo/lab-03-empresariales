from django import forms

from .models import Choice, Exam, Question


class ExamForm(forms.ModelForm):
    """Form to create and edit an Exam.

    'created_at' is excluded because it is set automatically
    (auto_now_add) and should not be edited by the user.
    """

    class Meta:
        model = Exam
        fields = ['title', 'description']


class QuestionForm(forms.ModelForm):
    """Form to create and edit a Question.

    'exam' is excluded on purpose: the parent exam is assigned by the
    view, not chosen by the user through this form.
    """

    class Meta:
        model = Question
        fields = ['text']


# Inline formset that manages a Question's Choice objects together
# with the question itself. 'extra=4' provides the 4 answer options
# required by the lab (step 9).
ChoiceFormSet = forms.inlineformset_factory(
    Question,
    Choice,
    fields=['text', 'is_correct'],
    extra=4,
)
