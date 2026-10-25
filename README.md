# onlinecourse_capstone

Django-based Online Course application featuring course details, lessons, mock exams, question management, submissions, and Bootstrap-styled pages.

This is a starter Django project for the Online Course assignment. Review the assignment instructions and test it locally before submitting.

## Included
- `onlinecourse/models.py`: Course, Lesson, Question, Choice, Submission models
- `onlinecourse/admin.py`: Django admin registrations
- `onlinecourse/views.py`: course details, exam submission, exam result views
- `onlinecourse/urls.py`: routes for course details and exam actions
- `onlinecourse/templates/onlinecourse/course_details_bootstrap.html`: Bootstrap course detail template
- `manage.py` and project settings

## Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python manage.py makemigrations onlinecourse
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/`.

This is a starter scaffold, not proof of a successful mock-exam attempt. To create the required `07-final.png`, run the app, complete an actual successful exam attempt, and capture the result page.
