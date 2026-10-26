from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .models import Choice, Course, Enrollment, Question, Submission


def registration_request(request):
    if request.method == "GET":
        return render(request, "onlinecourse/user_registration_bootstrap.html", {})
    username = request.POST.get("username", "").strip()
    password = request.POST.get("psw", "")
    first_name = request.POST.get("firstname", "")
    last_name = request.POST.get("lastname", "")
    if not username or not password:
        return render(request, "onlinecourse/user_registration_bootstrap.html",
                      {"message": "Username and password are required."})
    if User.objects.filter(username=username).exists():
        return render(request, "onlinecourse/user_registration_bootstrap.html",
                      {"message": "User already exists."})
    user = User.objects.create_user(username=username, first_name=first_name,
                                    last_name=last_name, password=password)
    login(request, user)
    return redirect("onlinecourse:index")


def login_request(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST.get("username", ""),
                            password=request.POST.get("psw", ""))
        if user is not None:
            login(request, user)
            return redirect("onlinecourse:index")
        return render(request, "onlinecourse/user_login_bootstrap.html",
                      {"message": "Invalid username or password."})
    return render(request, "onlinecourse/user_login_bootstrap.html", {})


def logout_request(request):
    logout(request)
    return redirect("onlinecourse:index")


def check_if_enrolled(user, course):
    return bool(user.is_authenticated and Enrollment.objects.filter(user=user, course=course).exists())


class CourseListView(generic.ListView):
    template_name = "onlinecourse/course_list_bootstrap.html"
    context_object_name = "course_list"

    def get_queryset(self):
        courses = Course.objects.order_by("-total_enrollment")[:10]
        for course in courses:
            course.is_enrolled = check_if_enrolled(self.request.user, course)
        return courses


class CourseDetailView(generic.DetailView):
    model = Course
    template_name = "onlinecourse/course_details_bootstrap.html"
    context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_enrolled"] = check_if_enrolled(self.request.user, self.object)
        context["questions"] = self.object.questions.prefetch_related("choices").all()
        context["lessons"] = self.object.lessons.all()
        return context


def enroll(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.user.is_authenticated:
        _, created = Enrollment.objects.get_or_create(
            user=request.user, course=course, defaults={"mode": "honor"}
        )
        if created:
            course.total_enrollment += 1
            course.save(update_fields=["total_enrollment"])
    return HttpResponseRedirect(reverse("onlinecourse:course_details", args=(course.id,)))


def extract_answers(request):
    answer_ids = []
    for key, value in request.POST.items():
        if key.startswith("choice_"):
            try:
                answer_ids.append(int(value))
            except (TypeError, ValueError):
                continue
    return answer_ids


def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    if request.method != "POST":
        return redirect("onlinecourse:course_details", pk=course_id)
    if not request.user.is_authenticated:
        return redirect("onlinecourse:login")

    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)
    selected_ids = extract_answers(request)
    valid_choices = Choice.objects.filter(id__in=selected_ids, question__course=course)
    submission.choices.set(valid_choices)
    return redirect("onlinecourse:show_exam_result",
                    course_id=course.id, submission_id=submission.id)


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(
        Submission, pk=submission_id, enrollment__course=course
    )
    selected_ids = set(submission.choices.values_list("id", flat=True))
    result_rows = []
    total_score = 0
    max_score = 0

    for question in course.questions.prefetch_related("choices").all():
        correct_ids = set(question.choices.filter(is_correct=True).values_list("id", flat=True))
        question_selected = selected_ids.intersection(
            set(question.choices.values_list("id", flat=True))
        )
        score = question.is_get_score(question_selected)
        total_score += score
        max_score += question.grade
        result_rows.append({
            "question": question,
            "choices": question.choices.all(),
            "selected_ids": question_selected,
            "correct_ids": correct_ids,
            "score": score,
        })

    grade = (100 * total_score / max_score) if max_score else 0
    return render(request, "onlinecourse/exam_result_bootstrap.html", {
        "course": course,
        "submission": submission,
        "results": result_rows,
        "grade": grade,
        "total_score": total_score,
        "max_score": max_score,
    })
