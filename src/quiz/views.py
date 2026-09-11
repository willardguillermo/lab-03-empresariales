from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from .forms import ChoiceFormSet, QuestionForm
from .models import Exam, Question


class ExamListView(ListView):
    """Displays every exam available in the system."""

    model = Exam
    template_name = 'quiz/exam_list.html'
    context_object_name = 'exams'


class ExamDetailView(DetailView):
    """Displays a single exam with its questions and their choices.

    The template can walk exam.questions.all() and, for each
    question, question.choices.all() thanks to the related_name
    values defined on the Question and Choice models.
    """

    model = Exam
    template_name = 'quiz/exam_detail.html'
    context_object_name = 'exam'


def _count_valid_correct_choices(formset):
    """Counts how many non-deleted, non-empty choices are correct.

    Extra blank forms (left empty by the user) produce an empty
    cleaned_data dict once the formset is valid, so they are skipped
    here instead of being counted as an unmarked choice.
    """
    correct_count = 0
    for form in formset:
        if form.cleaned_data.get('DELETE'):
            continue
        if not form.cleaned_data.get('text'):
            continue
        if form.cleaned_data.get('is_correct'):
            correct_count += 1
    return correct_count


def question_create(request, exam_id):
    """Creates a Question for the given Exam together with its Choices.

    QuestionForm and ChoiceFormSet (an inline formset bound to
    Question) are validated and saved together, in a single POST
    request:

    - QuestionForm validates the question text.
    - ChoiceFormSet validates each answer option (text, is_correct).
    - On top of that, a business rule that plain field validators
      cannot express because it depends on all the choices at once:
      exactly one non-empty choice must be marked as correct. This is
      checked manually, after both the form and the formset report
      themselves as individually valid.

    If the business rule fails, nothing is written to the database
    and the page is re-rendered with the bound form/formset, so the
    user does not lose what they already typed.
    """
    exam = get_object_or_404(Exam, pk=exam_id)

    # An unsaved Question with 'exam' already set is used as the
    # formset's parent instance, so both the form and the formset can
    # be bound to it before the question exists in the database.
    question = Question(exam=exam)
    formset_error = None

    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)
        formset = ChoiceFormSet(request.POST, instance=question)

        if question_form.is_valid() and formset.is_valid():
            correct_count = _count_valid_correct_choices(formset)

            if correct_count == 1:
                question = question_form.save()
                formset.instance = question
                formset.save()
                return redirect('quiz:exam_detail', pk=exam.pk)

            formset_error = (
                'Exactly one choice must be marked as correct '
                f'(found {correct_count}).'
            )
    else:
        question_form = QuestionForm(instance=question)
        formset = ChoiceFormSet(instance=question)

    context = {
        'exam': exam,
        'question_form': question_form,
        'formset': formset,
        'formset_error': formset_error,
    }
    return render(request, 'quiz/question_form.html', context)
