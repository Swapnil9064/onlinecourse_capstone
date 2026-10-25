from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from .models import Choice, Course, Question, Submission


def course_details(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, "onlinecourse/course_details_bootstrap.html", {"course": course})


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    questions = course.questions.prefetch_related("choices")
    if request.method != "POST":
        return render(request, "onlinecourse/exam.html", {"course": course, "questions": questions})

    score = 0
    total = questions.count()
    for question in questions:
        choice_id = request.POST.get(f"question_{question.id}")
        if not choice_id:
            continue
        choice = get_object_or_404(Choice, pk=choice_id, question=question)
        if choice.is_correct:
            score += 1
        if request.user.is_authenticated:
            Submission.objects.create(user=request.user, question=question, choice=choice)
    passed = total > 0 and score == total
    return render(request, "onlinecourse/exam_result.html", {
        "course": course, "score": score, "total": total, "passed": passed
    })


def show_exam_result(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    return render(request, "onlinecourse/exam_result.html", {
        "course": course,
        "score": request.session.get("last_exam_score", 0),
        "total": request.session.get("last_exam_total", course.questions.count()),
        "passed": request.session.get("last_exam_passed", False),
    })
