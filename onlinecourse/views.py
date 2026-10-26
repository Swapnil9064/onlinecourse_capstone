
def submit(request, course_id):
    from django.shortcuts import get_object_or_404, redirect
    from .models import Course, Enrollment, Choice, Submission

    course = get_object_or_404(Course, id=course_id)

    if request.method != "POST":
        return redirect("onlinecourse:course_details", pk=course_id)

    if not request.user.is_authenticated:
        return redirect("onlinecourse:login")

    enrollment = get_object_or_404(
        Enrollment,
        user=request.user,
        course=course,
    )

    submission = Submission.objects.create(enrollment=enrollment)

    selected_ids = []
    for key, value in request.POST.items():
        if key.startswith("choice_"):
            try:
                selected_ids.append(int(value))
            except (ValueError, TypeError):
                continue

    valid_choices = Choice.objects.filter(
        id__in=selected_ids,
        question__course=course,
    )
    submission.choices.set(valid_choices)

    return redirect(
        "onlinecourse:show_exam_result",
        course_id=course.id,
        submission_id=submission.id,
    )


def show_exam_result(request, course_id, submission_id):
    from django.shortcuts import get_object_or_404, render
    from .models import Course, Submission

    course = get_object_or_404(Course, id=course_id)

    submission = get_object_or_404(
        Submission,
        id=submission_id,
        enrollment__course=course,
        enrollment__user=request.user,
    )

    selected_ids = set(
        submission.choices.values_list("id", flat=True)
    )

    results = []
    total_score = 0
    max_score = 0

    for question in course.questions.prefetch_related("choices").all():
        question_choice_ids = set(
            question.choices.values_list("id", flat=True)
        )
        question_selected_ids = selected_ids.intersection(question_choice_ids)

        score = question.is_get_score(question_selected_ids)
        total_score += score
        max_score += question.grade

        results.append({
            "question": question,
            "choices": question.choices.all(),
            "selected_ids": question_selected_ids,
            "correct_ids": set(
                question.choices.filter(is_correct=True)
                .values_list("id", flat=True)
            ),
            "score": score,
        })

    grade = (total_score / max_score * 100) if max_score else 0

    return render(
        request,
        "onlinecourse/exam_result_bootstrap.html",
        {
            "course": course,
            "submission": submission,
            "results": results,
            "selected_ids": selected_ids,
            "total_score": total_score,
            "max_score": max_score,
            "grade": grade,
        },
    )
