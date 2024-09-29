import uuid
from django.db import models
from django.core.validators import EmailValidator, MinLengthValidator,RegexValidator
from django.contrib.auth.models import User
PHONE_REGEX = '^[0-9]{10}$'
NAME_REGEX = '^[A-Za-z ]+$'



# Create your models here.
class school_files(models.Model):
    name=models.CharField(max_length=50)
    
def __str__(self):
    return self.name

class school_file(models.Model):
    subject_name=models.CharField(max_length=100)
    year=models.CharField(max_length=50)
    course = models.CharField(max_length=100)   # New field for course name
    upload=models.ImageField(upload_to='materials/') 

    
    def __str__(self):
        return self.subject_name
    

class Student(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    COURSE_CHOICES = (
        ('science', 'science'),
        ('commerce', 'commerce'),
        ('humanitice', 'humanitice'),
       
        
    )

    name = models.CharField(max_length=200, validators=[
        MinLengthValidator(2),
        RegexValidator(regex=NAME_REGEX, message='Enter a valid name with alphabets and spaces only')
    ])
    email = models.EmailField(max_length=254, validators=[EmailValidator()])
    parent_name = models.CharField(max_length=200, validators=[MinLengthValidator(2)])
    parent_contact = models.CharField(max_length=15, validators=[
        MinLengthValidator(10),
        RegexValidator(regex=PHONE_REGEX, message='Enter a valid 10-digit phone number')
    ])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    course = models.CharField(max_length=10, choices=COURSE_CHOICES)
    
    date_of_birth = models.DateField()
    registration_date = models.DateTimeField(auto_now_add=True)
    student_image = models.ImageField(upload_to='students/images/', null=True, blank=True)
    roll_number = models.CharField(max_length=50, unique=True, blank=True)
    password = models.CharField(max_length=100, validators=[MinLengthValidator(6)])
    is_approved = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(Student, self).save(*args, **kwargs)
        if not self.roll_number:
            self.roll_number = '23HS' + str(self.id)
            super(Student, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
#feedback
class Feedback(models.Model):
    roll_number = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=200)
    date = models.DateField()
    feedback = models.TextField()
    admin_reply = models.TextField(blank=True, null=True)

    

class Teacher(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )

    DEPARTMENT_CHOICES = (
        ('science', 'Science'),
        ('commerce', 'Commerce'),
        ('humanities', 'Humanities'),
    )

    # Custom ID field
    teacher_id = models.CharField(max_length=10, unique=True, blank=True, editable=False, primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, validators=[
        MinLengthValidator(2),
        RegexValidator(regex=NAME_REGEX, message='Enter a valid name with alphabets and spaces only')
    ])
    email = models.EmailField(max_length=254, validators=[EmailValidator()])
    contact_number = models.CharField(max_length=15, validators=[
        MinLengthValidator(10),
        RegexValidator(regex=PHONE_REGEX, message='Enter a valid 10-digit phone number')
    ])
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    department = models.CharField(max_length=10, choices=DEPARTMENT_CHOICES)
    hire_date = models.DateField()
    profile_picture = models.ImageField(upload_to='teachers/images/', null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.teacher_id:
            # Generate a unique ID with 'SF' prefix
            self.teacher_id = 'SF' + str(uuid.uuid4().hex[:6]).upper()
        super(Teacher, self).save(*args, **kwargs)
        
    def can_score_student(self, student):
        """Check if the teacher can score the given student based on the course."""
        return self.department == student.course

    def __str__(self):
        return self.name
    

#teacher feedback
class TeacherFeedback(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='feedbacks')
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    course = models.CharField(max_length=100)
    date = models.DateField(auto_now_add=True)
    teaching_effectiveness = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    clarity_of_explanation = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    engagement = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    punctuality_time_management = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    interaction_with_students = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    feedback_support = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    classroom_management = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    teaching_aids_technology = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    positive_feedback = models.TextField(blank=True, null=True)
    areas_for_improvement = models.TextField(blank=True, null=True)
    additional_comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Feedback for {self.teacher.name} on {self.date}"
    
class TeacherScore(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(choices=[(i, i) for i in range(11)])  # Choices from 0 to 10
    comments = models.TextField(blank=True, null=True)  # Optional comments

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Score by {self.teacher.name} for {self.student.name}: {self.score}/10'