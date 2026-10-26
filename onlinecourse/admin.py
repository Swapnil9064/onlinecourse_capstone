from django.contrib import admin
from .models import Course, Lesson, Instructor, Learner, Enrollment, Question, Choice, Submission


class ChoiceInline(admin.StackedInline):
    model = Choice
    extra = 2


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 2


class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [LessonInline, QuestionInline]
    list_display = ("name", "pub_date", "total_enrollment")
    list_filter = ("pub_date",)
    search_fields = ("name", "description")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [ChoiceInline]
    list_display = ("question_text", "course", "grade")
    list_filter = ("course",)
    search_fields = ("question_text",)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    list_filter = ("course",)
    search_fields = ("title", "content")


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("choice_text", "question", "is_correct")
    list_filter = ("is_correct",)
    search_fields = ("choice_text",)


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "enrollment", "submitted_at")
    list_filter = ("submitted_at",)
    search_fields = ("enrollment__user__username", "enrollment__course__name")


admin.site.register(Instructor)
admin.site.register(Learner)
admin.site.register(Enrollment)
