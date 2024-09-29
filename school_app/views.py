import csv
from functools import wraps
from multiprocessing import AuthenticationError
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import  get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.contrib.auth import logout
from django.views import View
from .models import * 
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import UpdateView,CreateView,ListView
from .models import Student
from .forms import PasswordResetRequestForm, StudentForm, TeacherFeedbackForm, TeacherScoreForm, UserMessageForm
from django.core.mail import send_mail
from django.conf import settings
from .forms import MaterialSearchForm
from .models import school_file
from django.shortcuts import render, redirect
from .forms import TeacherForm
from django.contrib.auth.decorators import login_required
import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render
from .models import Student, school_file  # Ensure that you have imported your models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.http import HttpResponse
import os
import google.generativeai as genai
from .forms import UploadFileForm  # Make sure you have a form for file upload
import time
from nltk.sentiment import SentimentIntensityAnalyzer
from io import StringIO
import os
from django.shortcuts import render
from django.http import JsonResponse
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table, TableStyle
from reportlab.pdfgen import canvas
from groq import Groq
from django.contrib.auth.hashers import check_password
from django.db.models import Count
from django.contrib.auth import update_session_auth_hash
from .forms import PasswordChangeCustomForm

# Create your views here.
def index(request):
    return render(request, 'index.html')

def download(request):
    data=school_file.objects.all()
    print(data)
    return render(request, 'download.html', {'data':data})

def userview(request):
    data=school_file.objects.all()
    print(data)
    return render(request, 'userview.html', {'data':data})



# @login_required
def Admin_Dashboard(request):
    # Get the course filter from the request, if any
    selected_course = request.GET.get('course', None)

    # Data preparation for the bar chart
    student_counts = Student.objects.values('course').annotate(count=models.Count('id')).order_by('course')
    
    # Prepare data for Chart.js
    chart_data = {
        'labels': [item['course'] for item in student_counts],
        'data': [item['count'] for item in student_counts]
    }

    # Get all students grouped by course, filtered by the selected course if any
    if selected_course:
        students_by_course = Student.objects.filter(course=selected_course).order_by('name')
    else:
        students_by_course = Student.objects.all().order_by('course', 'name')

    # Get distinct list of courses for the dropdown
    courses = Student.objects.values_list('course', flat=True).distinct()

    return render(request, 'Admin_Dashboard.html', {
        'chart_data': chart_data,
        'students_by_course': students_by_course,
        'courses': courses,
        'selected_course': selected_course
    })
 
def about(request):
    return render(request, 'about.html')

def Login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_superuser:
                login(request, user)
                return redirect('upload')
            else:
                return render(request, 'Login.html', {'form': form, 'error_message': 'Invalid credentials'})

    else:
        form = AuthenticationError()

    return render(request, 'Login.html', {'form': form})

#update
class Update_detail(UpdateView):
    model=school_file
    fields='__all__'
    template_name='update.html'
    success_url=reverse_lazy('download')
    
#delete
def delete(request,pk):
    de=school_file.objects.get(id=pk)
    de.delete()

    return redirect('download')

#studentreigister
def register(request):
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/student-login/')
    else:
        form = StudentForm()

    return render(request, 'studentregister.html', {'form': form})




def approval(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        action = request.POST.get('action')
        
        # Ensure both student_id and action are provided
        if not student_id or not action:
            return render(request, 'approval.html', {'error': 'Invalid request.'})
        
        student = get_object_or_404(Student, id=student_id)

        if action == 'approve':
            student.is_approved = True
            student.save()

            # Send an email to the student
            send_mail(
                'Congratulations! Your registration has been approved ',
                f'Course {student.course}, Your User Roll Number is {student.roll_number} and your password is {student.password}.',
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )
            message = 'Student approved successfully and email sent.'

        elif action == 'reject':
            student.delete()
            send_mail(
                f'Sorry {student.name}, Your registration has been rejected.',
                'Unfortunately, your registration was not approved.',
                settings.EMAIL_HOST_USER,
                [student.email],
                fail_silently=False,
            )
            message = 'Student rejected successfully and email sent.'

        else:
            return render(request, 'approval.html', {'error': 'Invalid action.'})

        # Optionally add a success message to be displayed
        return render(request, 'approval.html', {'students': Student.objects.filter(is_approved=False), 'message': message})

    students = Student.objects.filter(is_approved=False)
    return render(request, 'approval.html', {'students': students})

#list of students in admin view
def studentview(request):
    data=Student.objects.all()
    print(data)
    return render(request, 'student_details.html', {'data':data})

#list of student
def registrationlist(request):
    data=Student.objects.all()
    print(data)
    return render(request, 'registrationlist.html', {'data':data})

def custom_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if 'student_id' in request.session or 'teacher_id' in request.session:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You must be logged in to view this page.")
            return redirect('student_login')  # Redirect to your login page
    return _wrapped_view

#studlogin
def studentlogin(request):
    if request.method == 'POST':
        login_type = request.POST.get('login_type')
        roll_number = request.POST.get('roll_number', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        if login_type == 'student':
            try:
                student = Student.objects.get(roll_number=roll_number)
                # Check if the password is hashed or in plain text
                if check_password(password, student.password):  # Check hashed password
                    request.session['student_id'] = student.id
                    messages.success(request, f"Welcome, {student.name}!")
                    return redirect('student_dashboard', student_id=student.id)
                else:
                    # Optionally, check if the password is plain text
                    if student.password == password:
                        # Save the plain-text password as hashed in the database
                        student.password = make_password(password)
                        student.save()
                        request.session['student_id'] = student.id
                        messages.success(request, f"Welcome, {student.name}!")
                        return redirect('student_dashboard', student_id=student.id)
                    else:
                        messages.error(request, "Invalid roll number or password. Please try again.")
            except Student.DoesNotExist:
                messages.error(request, "Invalid roll number or password. Please try again.")
        
        elif login_type == 'teacher':
            try:
                teacher = Teacher.objects.get(user__username=username)
                if teacher.user.check_password(password):
                    request.session['teacher_id'] = teacher.teacher_id
                    messages.success(request, f"Welcome, {teacher.name}!")
                    return redirect('teacher_dashboard', teacher_id=teacher.teacher_id)
                else:
                    messages.error(request, "Invalid username or password. Please try again.")
            except Teacher.DoesNotExist:
                messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'studentlogin.html')

def logout_view(request):
    # Clear session data for student and teacher
    if 'student_id' in request.session:
        del request.session['student_id']
    elif 'teacher_id' in request.session:
        del request.session['teacher_id']
    
    # Display a logout success message
    messages.success(request, "You have been logged out successfully.")
    
    # Redirect to the login page
    return redirect('/')

#search materials 

#@login_required
def material_search(request):
    if request.method == 'POST':
        form = MaterialSearchForm(request.POST)
        if form.is_valid():
            subject_name = form.cleaned_data.get('subject_name')
            year = form.cleaned_data.get('year')
            course = form.cleaned_data.get('course')

            # Filter the files based on the provided criteria
            materials = school_file.objects.all()

            if subject_name:
                materials = materials.filter(subject_name__icontains=subject_name)
            if year:
                materials = materials.filter(year__icontains=year)
            if course:
                materials = materials.filter(course__icontains=course)

            return render(request, 'listmaterials.html', {'materials': materials, 'form': form})
    else:
        form = MaterialSearchForm()

    return render(request, 'material_search.html', {'form': form})


#edit profile
class edit_student(UpdateView):
    model = Student
    fields = ['name', 'email', 'parent_name', 'parent_contact']
    template_name = 'edit_student.html'

    def post(self, request, *args, **kwargs):
        # Set the object before processing
        self.object = self.get_object()
        student = self.object

        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Check if the old password is correct
        if old_password:
            if not check_password(old_password, student.password):
                messages.error(request, "Old password is incorrect.")
                return self.form_invalid(self.get_form())
            
            # Check if the new passwords match
            if new_password1 != new_password2:
                messages.error(request, "New passwords do not match.")
                return self.form_invalid(self.get_form())

            # Set the new password
            student.password = make_password(new_password1)
            student.save()
            messages.success(request, "Password changed successfully.")

        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        # Use self.object (the student instance)
        return reverse_lazy('student_dashboard', kwargs={'student_id': self.object.id})
    
#student dashboard
@custom_login_required
def student_dashboard(request, student_id):
    student = get_object_or_404(Student, id=student_id)
    course = student.course
    teachers = Teacher.objects.filter(department=course)

    timetables = {
        'science': [
            ['Maths', 'Physics', 'Chemistry', 'Lunch', 'English', 'Computer', 'Lab'],
            ['Physics', 'Maths', 'English', 'Lunch', 'Chemistry', 'Computer', 'Lab'],
            ['Chemistry', 'Physics', 'Maths', 'Lunch', 'Computer', 'English', 'Lab'],
            ['English', 'Chemistry', 'Physics', 'Lunch', 'Maths', 'Computer', 'Lab'],
            ['Computer', 'English', 'Chemistry', 'Lunch', 'Physics', 'Maths', 'Lab'],
        ],
        'commerce': [
            ['Economics', 'Accounting', 'Business Studies', 'Lunch', 'English', 'Maths', 'Lab'],
            ['Accounting', 'Maths', 'Economics', 'Lunch', 'Business Studies', 'English', 'Lab'],
            ['Business Studies', 'Economics', 'Accounting', 'Lunch', 'English', 'Maths', 'Lab'],
            ['English', 'Business Studies', 'Maths', 'Lunch', 'Economics', 'Accounting', 'Lab'],
            ['Maths', 'English', 'Business Studies', 'Lunch', 'Economics', 'Accounting', 'Lab'],
        ],
        'humanities': [
            ['History', 'Geography', 'Political Science', 'Lunch', 'English', 'Sociology', 'Lab'],
            ['Geography', 'History', 'English', 'Lunch', 'Political Science', 'Sociology', 'Lab'],
            ['Political Science', 'Geography', 'History', 'Lunch', 'Sociology', 'English', 'Lab'],
            ['English', 'Political Science', 'Geography', 'Lunch', 'History', 'Sociology', 'Lab'],
            ['Sociology', 'English', 'Political Science', 'Lunch', 'Geography', 'History', 'Lab'],
        ],
    }

    timetable = timetables.get(course, [])

    if request.method == 'POST':
        form = TeacherFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.student = student
            feedback.teacher = Teacher.objects.get(teacher_id=request.POST.get('teacher_id'))
            feedback.save()
            return redirect('student_dashboard', student_id=student.id)
    else:
        form = TeacherFeedbackForm()

    return render(request, 'student_dashboard.html', {
        'student': student,
        'timetable': timetable,
        'teachers': teachers,
        'form': form,
    })


from datetime import date, timedelta
@custom_login_required
def feedback_form(request):
    student_id = request.GET.get('student_id')
    student = get_object_or_404(Student, id=student_id)

    # Get teachers based on the student's course
    all_teachers = Teacher.objects.filter(department=student.course)

    # Exclude teachers for whom feedback has been submitted within the last month
    recent_feedback_teachers = TeacherFeedback.objects.filter(
        student=student,
        date__gte=date.today() - timedelta(days=30)
    ).values_list('teacher__teacher_id', flat=True)

    teachers = all_teachers.exclude(teacher_id__in=recent_feedback_teachers)

    if request.method == 'POST':
        form = TeacherFeedbackForm(request.POST)
        if form.is_valid():
            teacher_id = request.POST.get('teacher_id')
            teacher = get_object_or_404(Teacher, teacher_id=teacher_id)
            last_feedback = TeacherFeedback.objects.filter(
                student=student, teacher=teacher
            ).order_by('-date').first()

            if last_feedback:
                today = date.today()  # Use date.today() correctly
                if (today - last_feedback.date).days < 30:
                    return render(request, 'feedback_form.html', {
                        'student': student,
                        'teachers': teachers,
                        'form': form,
                        'error_message': 'You can only submit feedback once every month.',
                    })

            feedback = form.save(commit=False)
            feedback.student = student
            feedback.teacher = teacher
            feedback.save()
            return render(request, 'feedback_form.html', {
                'student': student,
                'teachers': teachers,
                'form': form,
                'success_message': 'Feedback submitted successfully!',
            })
    else:
        form = TeacherFeedbackForm()

    return render(request, 'feedback_form.html', {
        'student': student,
        'teachers': teachers,
        'form': form,
    })

def listmaterials(request):
    student = request.user.student  # Assuming the student is logged in
    study_materials = student.study_materials.all()

    context = {'study_materials': study_materials}
    return render(request, 'userview.html', {'student': student, 'study_materials': study_materials})


def admin_logout(request):
    logout(request)
    # Redirect to a specific page after logout (you can change this to your desired URL)
    return redirect('Login') 

def feedback_view(request):
    return render(request, 'feedback.html')

def Contact(request):
    return render(request, 'Contact.html')

def staff(request):
    return render(request, 'staff.html')

def coures(request):
    return render(request, 'course.html')

@login_required(login_url='Login')
def register_teacher(request):
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            # Check if the email is already used by a student
            if Student.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already used by a student.')
            # Check if the email is already used by another user
            elif User.objects.filter(email=email).exists():
                form.add_error('email', 'This email is already used by another user.')
            else:
                # Generate a unique username
                username = email.split('@')[0]
                if User.objects.filter(username=username).exists():
                    username = username + str(uuid.uuid4().hex[:4])
                
                # Create the User instance
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # Save the Teacher instance
                teacher = form.save(commit=False)
                teacher.user = user
                teacher.teacher_id = 'SF' + str(uuid.uuid4().hex[:6]).upper()
                teacher.save()
                
                # Send email with user details
                subject = 'Your Teacher Account Details'
                message = (
                    f'Hello {teacher.name},\n\n'
                    f'Your teacher account has been created successfully. Here are your login details:\n'
                    f'Username: {user.username}\n'
                    f'Password: {password}\n\n'
                    f'Please log in and change your password immediately.'
                )
                
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [teacher.email],
                    fail_silently=False,
                )
                
                # Redirect to the teacher list or any other view
                return redirect('upload')
    else:
        form = TeacherForm()
    
    return render(request, 'teacher_form.html', {'form': form})

@custom_login_required
def teacher_dashboard(request, teacher_id):
    teacher = get_object_or_404(Teacher, teacher_id=teacher_id)

    # Filter students based on the teacher's department and the student's course
    if teacher.department == 'science':
        students = Student.objects.filter(course='science', is_approved=True)
    elif teacher.department == 'commerce':
        students = Student.objects.filter(course='commerce', is_approved=True)
    elif teacher.department == 'humanities':
        students = Student.objects.filter(course='humanities', is_approved=True)
    else:
        students = Student.objects.none()  # No students if department is not matched

    # Retrieve all feedback records for this teacher
    feedbacks = TeacherFeedback.objects.filter(teacher=teacher)

    if feedbacks:
        # Calculate average performance score and composite sentiment score
        total_performance_score = 0
        total_positive_sentiment = 0
        total_improvement_sentiment = 0
        total_additional_comments_sentiment = 0
        feedback_count = len(feedbacks)

        for feedback in feedbacks:
            total_performance_score += (
                feedback.teaching_effectiveness +
                feedback.clarity_of_explanation +
                feedback.engagement +
                feedback.punctuality_time_management +
                feedback.interaction_with_students +
                feedback.feedback_support +
                feedback.classroom_management +
                feedback.teaching_aids_technology
            )

            total_positive_sentiment += analyze_sentiment(feedback.positive_feedback) if feedback.positive_feedback else 0
            total_improvement_sentiment += analyze_sentiment(feedback.areas_for_improvement) if feedback.areas_for_improvement else 0
            total_additional_comments_sentiment += analyze_sentiment(feedback.additional_comments) if feedback.additional_comments else 0

        avg_performance_score = total_performance_score / (feedback_count * 8)  # Average score out of 10
        composite_sentiment_score = (
            (total_positive_sentiment + total_improvement_sentiment + total_additional_comments_sentiment) / (feedback_count * 3)  # Average sentiment score
        )
    else:
        avg_performance_score = 0
        composite_sentiment_score = 0

    # Prepare data for the line chart (e.g., scores over time)
    performance_data = [
        {
            'date': feedback.date,  # Assuming there's a date field in feedback
            'score': (
                feedback.teaching_effectiveness +
                feedback.clarity_of_explanation +
                feedback.engagement +
                feedback.punctuality_time_management +
                feedback.interaction_with_students +
                feedback.feedback_support +
                feedback.classroom_management +
                feedback.teaching_aids_technology
            ) / 8  # Average score per feedback
        }
        for feedback in feedbacks
    ]

    context = {
        'teacher': teacher,
        'students': students,
        'avg_performance_score': avg_performance_score,
        'composite_sentiment_score': composite_sentiment_score,
        'performance_data': performance_data,
    }

    return render(request, 'teacher_dashboard.html', context)



#note maker
client = Groq(api_key="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")

@custom_login_required
def generate_note_view(request):
    if request.method == "POST":
        # Extract user input from the POST request
        topic = request.POST.get("topic")
        subtopic = request.POST.get("subtopic")
        concept = request.POST.get("concept")
        detail_level = request.POST.get("detail_level")

        # Prepare the messages for the Groq API
        messages = [
            {
                "role": "user",
                "content": f"generate the note content based on the user input and include the field of study from that generate the note"
            },
            {
                "role": "assistant",
                "content": f"I'll be happy to help! Here's the information:\n\n1. Topic: {topic}\n2. Subtopic: {subtopic}\n3. Concept: {concept}\n4. Level of Detail: {detail_level}"
            }
        ]

        # Call the Groq API to generate the note
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=messages,
            temperature=1,
            max_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )

        # Collect the generated note content
        note_content = ""
        for chunk in completion:
            note_content += chunk.choices[0].delta.content or ""

        # Check if the user requested to download as PDF
        if request.POST.get("download") == "pdf":
            # Create PDF in memory
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            story.append(Paragraph("Generated Note", styles['Title']))
            story.append(Spacer(1, 12))

            # Add details as a table
            data = [
                ['Topic:', topic],
                ['Subtopic:', subtopic],
                ['Concept:', concept],
                ['Level of Detail:', detail_level]
            ]
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ]))
            story.append(table)
            story.append(Spacer(1, 12))

            # Add the note content
            story.append(Paragraph("Note Content:", styles['Heading2']))
            story.append(Spacer(1, 12))
            story.append(Paragraph(note_content, styles['BodyText']))

            # Build the PDF
            doc.build(story)

            # Get the value of the BytesIO buffer and write it to the response
            buffer.seek(0)
            response = HttpResponse(buffer, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="generated_note.pdf"'
            return response

        # Return the generated note as a JSON response
        return JsonResponse({"note_content": note_content})

    # Render the input form if the request method is GET
    return render(request, "generate_note.html")

def teacher_list(request):
    department = request.GET.get('department')
    if department:
        teachers = Teacher.objects.filter(department=department)
    else:
        teachers = Teacher.objects.all()

    teacher_scores = []

    for teacher in teachers:
        # Retrieve all feedback records for this teacher
        feedbacks = TeacherFeedback.objects.filter(teacher=teacher)

        if feedbacks:
            # Calculate average performance score and composite sentiment score
            total_performance_score = 0
            total_positive_sentiment = 0
            total_improvement_sentiment = 0
            total_additional_comments_sentiment = 0
            feedback_count = len(feedbacks)

            for feedback in feedbacks:
                total_performance_score += (
                    feedback.teaching_effectiveness +
                    feedback.clarity_of_explanation +
                    feedback.engagement +
                    feedback.punctuality_time_management +
                    feedback.interaction_with_students +
                    feedback.feedback_support +
                    feedback.classroom_management +
                    feedback.teaching_aids_technology
                )

                total_positive_sentiment += analyze_sentiment(feedback.positive_feedback) if feedback.positive_feedback else 0
                total_improvement_sentiment += analyze_sentiment(feedback.areas_for_improvement) if feedback.areas_for_improvement else 0
                total_additional_comments_sentiment += analyze_sentiment(feedback.additional_comments) if feedback.additional_comments else 0

            avg_performance_score = total_performance_score / (feedback_count * 8)  # Average score out of 10
            composite_sentiment_score = (
                (total_positive_sentiment + total_improvement_sentiment + total_additional_comments_sentiment) / (feedback_count * 3)  # Average sentiment score
            )

            teacher_scores.append({
                'teacher': teacher,
                'avg_performance_score': avg_performance_score,
                'composite_sentiment_score': composite_sentiment_score
            })
        else:
            teacher_scores.append({
                'teacher': teacher,
                'avg_performance_score': 0,
                'composite_sentiment_score': 0
            })

    context = {
        'teacher_scores': teacher_scores,
        'department_choices': Teacher.DEPARTMENT_CHOICES
    }
    return render(request, 'teacher_list.html', context)

# Configure the Gemini API with your API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    file = genai.upload_file(path, mime_type=mime_type)
    return file

def wait_for_files_active(files):
    """Waits for the given files to be active."""
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")

def process_pdf(request):
    if request.method == 'POST' and request.FILES['pdf_file']:
        # Save the uploaded file
        pdf_file = request.FILES['pdf_file']
        fs = FileSystemStorage()
        filename = fs.save(pdf_file.name, pdf_file)
        file_path = fs.path(filename)

        # Upload to Gemini
        gemini_file = upload_to_gemini(file_path, mime_type="application/pdf")
        wait_for_files_active([gemini_file])

        # Create the model and chat session
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start chat session and generate summary
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [gemini_file],
                },
            ]
        )

        # Generate a response (e.g., summary or MCQs)
        response = chat_session.send_message("Summarize the content and generate MCQs.")

        # Clean up: delete the file from the server
        os.remove(file_path)

        # Render the result in the template
        return render(request, 'result.html', {
            'summary': response.text
        })

    return render(request, 'upload.html')



def analyze_sentiment(text):
    if not text:
        return 0

    sia = SentimentIntensityAnalyzer()
    sentiment_score = sia.polarity_scores(text)['compound']
    return sentiment_score

def feedback_analysis(request):
    # Retrieve all feedback records
    feedbacks = TeacherFeedback.objects.all()

    results = []
    labels = []
    avg_performance_scores = []
    composite_sentiment_scores = []

    for feedback in feedbacks:
        # Perform sentiment analysis
        positive_sentiment = analyze_sentiment(feedback.positive_feedback) if feedback.positive_feedback else 0
        improvement_sentiment = analyze_sentiment(feedback.areas_for_improvement) if feedback.areas_for_improvement else 0
        additional_comments_sentiment = analyze_sentiment(feedback.additional_comments) if feedback.additional_comments else 0

        # Calculate average performance score
        avg_performance_score = (
            (feedback.teaching_effectiveness +
             feedback.clarity_of_explanation +
             feedback.engagement +
             feedback.punctuality_time_management +
             feedback.interaction_with_students +
             feedback.feedback_support +
             feedback.classroom_management +
             feedback.teaching_aids_technology) / 8
        )

        # Calculate composite sentiment score
        composite_sentiment_score = (
            positive_sentiment + improvement_sentiment + additional_comments_sentiment
        ) / 3  # Adjust this formula as needed

        results.append({
            'teacher': feedback.teacher.name,
            'avg_performance_score': avg_performance_score,
            'positive_feedback_sentiment': positive_sentiment,
            'areas_for_improvement_sentiment': improvement_sentiment,
            'additional_comments_sentiment': additional_comments_sentiment,
            'composite_sentiment_score': composite_sentiment_score
        })

        # Prepare data for the chart
        labels.append(feedback.teacher.name)
        avg_performance_scores.append(avg_performance_score)
        composite_sentiment_scores.append(composite_sentiment_score)

    # Check if the request is for downloading a CSV file
    if 'download_csv' in request.GET:
        return export_to_csv(results)

    return render(request, 'feedback_analysis.html', {
        'results': results,
        'labels': labels,
        'avg_performance_scores': avg_performance_scores,
        'composite_sentiment_scores': composite_sentiment_scores
    })

def export_to_csv(results):
    # Create a CSV file in memory
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Teacher', 'Average Performance Score', 'Positive Feedback Sentiment',
        'Areas for Improvement Sentiment', 'Additional Comments Sentiment',
        'Composite Sentiment Score'
    ])

    for result in results:
        writer.writerow([
            result['teacher'],
            result['avg_performance_score'],
            result['positive_feedback_sentiment'],
            result['areas_for_improvement_sentiment'],
            result['additional_comments_sentiment'],
            result['composite_sentiment_score']
        ])

    # Set up the HTTP response
    output.seek(0)
    response = HttpResponse(output, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="feedback_analysis.csv"'
    return response

import os
import time
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from django.views import View
from django.core.files.storage import default_storage

# Configure the Gemini API with your API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-pro",
    generation_config=generation_config,
)

def upload_to_gemini(file_path, mime_type=None):
    try:
        file = genai.upload_file(file_path, mime_type=mime_type)
        return file
    except Exception as e:
        raise Exception(f"Error uploading file to Gemini: {str(e)}")

def wait_for_files_active(files):
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")

def chat_view(request):
    response_text = ""
    if request.method == 'POST':
        form = UserMessageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES.get('file')
            question = form.cleaned_data['question']

            if uploaded_file:
                if not uploaded_file.content_type in ['text/plain', 'application/pdf']:
                    response_text = "Invalid file type. Please upload a text or PDF file."
                else:
                    try:
                        file_path = default_storage.save(uploaded_file.name, uploaded_file)
                        full_file_path = default_storage.path(file_path)

                        files = [upload_to_gemini(full_file_path)]
                        wait_for_files_active(files)

                        chat_session = model.start_chat(
                            history=[
                                {
                                    "role": "user",
                                    "parts": [
                                        files[0],
                                        question,
                                    ],
                                },
                            ]
                        )

                        response = chat_session.send_message(question)
                        response_text = response.text

                    except Exception as e:
                        response_text = f"Error during chat processing: {str(e)}"

                    finally:
                        if os.path.exists(full_file_path):
                            os.remove(full_file_path)
            else:
                response_text = "No file uploaded. Please upload a file to proceed."

    else:
        form = UserMessageForm()

    return render(request, 'chat.html', {'form': form, 'response_text': response_text})

import secrets
import base64

def generate_token_and_uid(student_id):
    # Generate a secure random token
    token = secrets.token_urlsafe(16)  # 16 bytes should be sufficient

    # Encode the student ID to base64
    uid = base64.urlsafe_b64encode(str(student_id).encode()).decode()

    return token, uid
#https://eduai-g6oj.onrender.com

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                student = Student.objects.get(email=email)
                token, uid = generate_token_and_uid(student.pk)
                reset_link = f"http://127.0.0.1:8000/reset-password/{uid}/{token}/"
                
                send_mail(
                    'Password Reset Request',
                    f'Click the link to reset your password: {reset_link}',
                    'bimalbabu720@gmail.com',
                    [email],
                    fail_silently=False,
                )
                return redirect('student_login')  # Redirect to a success page
            except Student.DoesNotExist:
                form.add_error('email', 'This email is not registered.')
    else:
        form = PasswordResetRequestForm()
    return render(request, 'password_reset_request.html', {'form': form})

from django.contrib.auth.hashers import make_password

def password_reset_confirm(request, uidb64, token):
    error_message = None  # Initialize error_message

    try:
        # Decode uid from base64
        student_id = int(base64.urlsafe_b64decode(uidb64).decode())
        student = Student.objects.get(pk=student_id)

        # Here you would normally verify the token (implement your verification logic)
        if token:  # Replace with your token verification logic
            if request.method == "POST":
                new_password = request.POST.get('new_password', '').strip()
                confirm_password = request.POST.get('confirm_password', '').strip()

                # Check if both passwords match
                if new_password == confirm_password:
                    student.password = make_password(new_password)  # Hash the new password
                    student.save()
                    return redirect('student_login')  # Redirect to a success page
                else:
                    error_message = "Passwords do not match."
        else:
            error_message = "Invalid token."

    except (ValueError, TypeError, Student.DoesNotExist):
        error_message = "Invalid request."

    return render(request, 'password_reset_confirm.html', {'student': student, 'error_message': error_message})

# View to generate the student report
def student_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    gender = request.GET.get('gender')  # Retrieve gender from the request

    students = Student.objects.all()

    # Filter by date range if both start_date and end_date are provided
    if start_date and end_date:
        students = students.filter(registration_date__date__range=[start_date, end_date])

    # Filter by gender if a gender is selected
    if gender:
        students = students.filter(gender=gender)

    # Count students by course
    student_count_by_course = students.values('course').annotate(count=Count('course'))

    # Convert the course data into a more readable format using COURSE_CHOICES
    student_count_by_course_dict = {
        dict(Student.COURSE_CHOICES)[course['course']]: course['count']
        for course in student_count_by_course
    }

    context = {
        'students': students,
        'student_count_by_course': student_count_by_course_dict,
    }

    return render(request, 'student_report.html', context)
# CSV Download View
def download_csv(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    students = Student.objects.all()

    if start_date and end_date:
        students = students.filter(registration_date__date__range=[start_date, end_date])

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="student_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Roll Number', 'Name', 'Email', 'Parent Name', 'Parent Contact', 'Gender', 'Course', 'Date of Birth', 'Registration Date', 'Approval Status'])

    for student in students:
        writer.writerow([
            student.roll_number,
            student.name,
            student.email,
            student.parent_name,
            student.parent_contact,
            student.get_gender_display(),
            student.get_course_display(),
            student.date_of_birth,
            student.registration_date,
            'Approved' if student.is_approved else 'Pending'
        ])

    return response

# PDF Download View
def download_pdf(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    students = Student.objects.all()

    if start_date and end_date:
        students = students.filter(registration_date__date__range=[start_date, end_date])

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="student_report.pdf"'

    p = canvas.Canvas(response)
    p.drawString(100, 800, "Student Report")
    y = 750

    for student in students:
        p.drawString(100, y, f"Roll Number: {student.roll_number} | Name: {student.name} | Course: {student.get_course_display()}")
        y -= 20

    p.showPage()
    p.save()
    return response