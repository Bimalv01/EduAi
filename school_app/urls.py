from django.urls import include, path
from .views import  *
from . import views 

urlpatterns = [
    path('', views.index, name='index'),
    path('download/', views.download, name='download'),
    path('userview/',views.userview,name='userview'),
    path('Login/',views.Login, name='Login'),
    path('Admin_Dashboard/', views.Admin_Dashboard, name='upload'),
    path('about/', views.about, name='about'),
    path('logout/', admin_logout, name='a_logout'),
    path('accounts/', include("django.contrib.auth.urls")),
    path('delete/<int:pk>/', views.delete, name='delete'),  # Delete product
    path('update/<int:pk>', views.Update_detail.as_view()),  # Delete product
    path('logout_view/', logout_view, name='logout_view'),
    path('register/',views.register, name='register'),
    path('approval/',views.approval, name='approval'),
    path('studentdetails/', views.studentview, name='studentview'),
    path('edit_student/<int:pk>/', views.edit_student.as_view()),
 
    path('student-login/', views.studentlogin, name='student_login'),
    path('registrationlist/',views.registrationlist,name='registrationlist'),
    path('material-search/', material_search, name='material_search'),
    path('student_dashboard/<int:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('listmaterials/', views.listmaterials, name='listmaterials'),
    path('teacher/dashboard/<str:teacher_id>/', teacher_dashboard, name='teacher_dashboard'),

    path('Contact/',Contact, name='Contact'),
    path('staff/', staff, name='staff'),
    path('coures/',coures, name='coures'),
    
    #teacher 
    path('Teacher_register/', register_teacher, name='register_teacher'),
    path('teachers/', teacher_list, name='teacher_list'),
    path('teacher-dashboard/<str:teacher_id>/', views.teacher_dashboard, name='teacher_dashboard'),
    path('feedback-analysis/', feedback_analysis, name='feedback_analysis'),
    path('feedback_form/', views.feedback_form, name='feedback_form'),

    #note maker 
    path('generate-note/',views.generate_note_view, name='generate_note'),
    path('note-upload/', views.process_pdf, name='upload_view'),
    path('chat/', chat_view, name='chat_view'),

    #forgot password 
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('reset-password/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    
    #report 
    path('student-report/', student_report, name='student_report'),
    path('student-report/download-csv/', download_csv, name='download_csv'),
    path('student-report/download-pdf/', download_pdf, name='download_pdf'),
   
]
