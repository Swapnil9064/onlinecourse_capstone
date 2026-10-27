from django.shortcuts import get_object_or_404, redirect, render
from .models import Choice, Course, Enrollment, Submission

def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)

    if not request.user.is_authenticated:
        return redirect("onlinecourse:login")

    submission = get_object_or_404(
        Submission,
        pk=submission_id,
        enrollment__course=course,
        enrollment__user=request.user,
    )

    selected_ids = set(
        submission.choices.values_list("id", flat=True)
    )

    results = []
    total_score = 0
    possible_score = 0

    for question in course.questions.prefetch_related("choices").all():
        question_choice_ids = set(
            question.choices.values_list("id", flat=True)
        )

        question_selected_ids = selected_ids.intersection(
            question_choice_ids
        )

        correct_ids = set(
            question.choices.filter(is_correct=True)
            .values_list("id", flat=True)
        )

        score = question.is_get_score(question_selected_ids)

        total_score += score
        possible_score += question.grade

        results.append({
            "question": question,
            "choices": question.choices.all(),
            "selected_ids": question_selected_ids,
            "correct_ids": correct_ids,
            "score": score,
        })

    grade = (
        (total_score / possible_score) * 100
        if possible_score > 0
        else 0
    )

    context = {
        "course": course,
        "submission": submission,
        "results": results,
        "selected_ids": selected_ids,
        "total_score": total_score,
        "possible_score": possible_score,
        "grade": grade,
    }

    return render(
        request,
        "onlinecourse/exam_result.html",
        context,
    )
