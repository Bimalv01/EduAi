from django import forms
from .models import *


class DateInput(forms.DateInput):
    input_type = 'date'

class StudentForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(max_length=100)

    class Meta:
        model = Student
        exclude = ['roll_number', 'is_approved']
        widgets = {
            'date_of_birth': DateInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data
#
class MaterialSearchForm(forms.Form):
    subject_name = forms.CharField(max_length=100, required=False)
    # year = forms.CharField(max_length=50, required=False)
    # course=forms.CharField(max_length=50, required=False)

class TeacherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    class Meta:
        model = Teacher
        fields = ['name', 'email', 'contact_number', 'gender', 'department', 'hire_date', 'profile_picture']

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email']
        )
        teacher = super().save(commit=False)
        teacher.user = user
        if commit:
            teacher.save()
        return teacher
            
class UploadFileForm(forms.Form):
    pdf_file = forms.FileField(label='Select a PDF file')


class TeacherFeedbackForm(forms.ModelForm):
    class Meta:
        model = TeacherFeedback
        fields = [
            'teaching_effectiveness',
            'clarity_of_explanation',
            'engagement',
            'punctuality_time_management',
            'interaction_with_students',
            'feedback_support',
            'classroom_management',
            'teaching_aids_technology',
            'positive_feedback',
            'areas_for_improvement',
            'additional_comments',
        ]
        widgets = {
            'positive_feedback': forms.Textarea(attrs={'rows': 2}),
            'areas_for_improvement': forms.Textarea(attrs={'rows': 2}),
            'additional_comments': forms.Textarea(attrs={'rows': 2}),
        }
        labels = {
            'teaching_effectiveness': 'Teaching Effectiveness (1-5)',
            'clarity_of_explanation': 'Clarity of Explanation (1-5)',
            'engagement': 'Engagement (1-5)',
            'punctuality_time_management': 'Punctuality & Time Management (1-5)',
            'interaction_with_students': 'Interaction with Students (1-5)',
            'feedback_support': 'Feedback Support (1-5)',
            'classroom_management': 'Classroom Management (1-5)',
            'teaching_aids_technology': 'Use of Teaching Aids & Technology (1-5)',
            'positive_feedback': 'Positive Feedback',
            'areas_for_improvement': 'Areas for Improvement',
            'additional_comments': 'Additional Comments',
        }

class UserMessageForm(forms.Form):
    file = forms.FileField()
    question = forms.CharField(widget=forms.Textarea)

class TeacherScoreForm(forms.ModelForm):
    class Meta:
        model = TeacherScore
        fields = ['score', 'comments']  # Only include fields from the user input

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop('teacher', None)
        self.student = kwargs.pop('student', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        teacher_score = super().save(commit=False)
        if self.teacher:
            teacher_score.teacher = self.teacher
        if self.student:
            teacher_score.student = self.student
        if commit:
            teacher_score.save()
        return teacher_score
    
class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Enter your email", max_length=254)

class PasswordChangeCustomForm(forms.Form):
    old_password = forms.CharField(
        label="Old Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="New Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="Confirm New Password", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The new passwords do not match.")

        return cleaned_data
