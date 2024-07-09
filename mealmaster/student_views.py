import datetime
from django.shortcuts import render,redirect
from app.models import Student_Notification,Student,Student_Feedback,Mess_off_leave,Billing
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseBadRequest,HttpResponse
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import pdfencrypt
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Spacer

from io import BytesIO

def Home(request):
    return render(request,'student/home.html')

def STUDENT_NOTIFICATION(request):
    student = Student.objects.filter(user = request.user.id)
    for i in student:
        #print(student)
        student_id = i.id
        notification = Student_Notification.objects.filter(student_id = student_id)
        context = {
            'notification':notification,
        }
    return render(request,'student/notification.html',context)

def STUDENT_NOTIFICATION_MARK_DONE(request,status):
    notification = Student_Notification.objects.get(id = status)
    notification.status = 1
    notification.save()

    return redirect('student_notification')

def STUDENT_FEEDBACK(request):
    student_id = Student.objects.get(user = request.user.id)
    feedback_history = Student_Feedback.objects.filter(student_id = student_id)

    context ={
        'feedback_history':feedback_history,
        
    }
    return render(request,'student/feedback.html',context)


def STUDENT_FEEDBACK_SAVE(request):

    if request.method == "POST":
        feedback = request.POST.get('feedback')

        student = Student.objects.get(user = request.user.id)
        feedbacks = Student_Feedback(
            student_id = student,
            feedback = feedback,
            feedback_reply ="",
        )
        feedbacks.save()
        return redirect('student_feedback')



def STUDENT_MESS_OFF(request):
    student = Student.objects.get(user = request.user.id)
    mess_off_history = Mess_off_leave.objects.filter(student_id = student)
    
    context = {
        'mess_off_history':mess_off_history,
    }

    return render(request,'student/mess_off.html',context)



# def STUDENT_MESS_LEAVE_SAVE(request):
#     if request.method =="POST":
#         off_date = request.POST.get('off_date')
#         on_date = request.POST.get('on_date')
#         leave_message = request.POST.get('leave_message')
#        # days = abs(on_date-off_date)-1

#         student_id = Student.objects.get(user = request.user.id)
#         mess_off_leave = Mess_off_leave(
#             student_id = student_id,
#             off_date = off_date,
#             on_date = on_date,
#             message = leave_message,
#             #days=days
            
#         )
#         mess_off_leave.save()
#         messages.success(request,'mess off leave applied successfully')
#         return redirect('student_mess_off')


# def STUDENT_MESS_LEAVE_SAVE(request):
#     if request.method == "POST":
#         off_date_str = request.POST.get('off_date')
#         on_date_str = request.POST.get('on_date')
#         leave_message = request.POST.get('leave_message')

#         # Parse the off_date and on_date strings into datetime objects
#         off_date = timezone.make_aware(datetime.datetime.strptime(off_date_str, '%Y-%m-%d'))
#         on_date = timezone.make_aware(datetime.datetime.strptime(on_date_str, '%Y-%m-%d'))

#         # Check that the leave period is at least one day
        
#         if (on_date - off_date).days < 1:
#             return HttpResponseBadRequest('The leave period must be at least one day.')

#         # Check that the leave period starts from today or a future date
#         today = datetime.datetime.now().date()
#         off_date = datetime.datetime.strptime(request.POST.get('off_date'), "%Y-%m-%d").date()
#         if off_date < today:
#             return HttpResponseBadRequest('The leave period cannot start from a past date.')

#         student_id = Student.objects.get(user=request.user.id)
#         mess_off_leave = Mess_off_leave(
#             student_id=student_id,
#             off_date=off_date,
#             on_date=on_date,
#             message=leave_message,
#         )
#         mess_off_leave.save()
#         messages.success(request, 'Mess off leave applied successfully')
#         return redirect('student_mess_off')





def STUDENT_MESS_LEAVE_SAVE(request):
    if request.method == "POST":
        off_date = request.POST.get('off_date')
        on_date = request.POST.get('on_date')
        leave_message = request.POST.get('leave_message')

        student_id = Student.objects.get(user=request.user.id)
        today = timezone.now().date()

        try:
            off_date = datetime.datetime.strptime(off_date, "%Y-%m-%d").date()
            on_date = datetime.datetime.strptime(on_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, "Invalid date format. Please use YYYY-MM-DD format.")
            return redirect('student_mess_off')

        if off_date <= today:
            messages.error(request, "Leave cannot be applied for past or present dates.")
            return redirect('student_mess_off')

        if off_date >= on_date:
            messages.error(request, "Start date must be before end date.")
            return redirect('student_mess_off')
        
        
        # Check if student has already applied for leave during requested dates
        leaves = Mess_off_leave.objects.filter(student_id=student_id)
        for leave in leaves:
            if off_date <= leave.on_date and on_date >= leave.off_date:
                messages.error(request, "Leave already applied for overlapping dates.")
                return redirect('student_mess_off')

        days = (on_date - off_date).days + 1

        mess_off_leave = Mess_off_leave(
            student_id=student_id,
            off_date=off_date,
            on_date=on_date,
            message=leave_message,
            days=days
        )
        mess_off_leave.save()
        messages.success(request, 'Mess off leave applied successfully.')
        return redirect('student_mess_off')








# def view_bills(request):
#    student = request.user.student
#    bills = Billing.objects.filter(student=student)
#    context = {'student': student, 'bills': bills}
#    return render(request, 'student/view_bills.html', context)


from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate
from io import BytesIO

from reportlab.platypus import Spacer

def generate_bills_pdf(student):
    # Get student details
    student_name = student.user.first_name + " " + student.user.last_name if hasattr(student.user, 'first_name') and hasattr(student.user, 'last_name') else ""
    student_address = student.address
    student_gender = student.gender
    student_roll_number = student.roll_number
    student_room_number = student.room_number
    student_phone_number = student.phone_number

    # Create a buffer for the PDF
    buffer = BytesIO()

    # Create a PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Title
    title = "MessMinder Mess Bill"
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_paragraph = Paragraph(title, title_style)
    
    # Watermark
    watermark_text = "MESSMINDER"
    watermark_style = styles['Normal']
    watermark_style.alignment = TA_CENTER

    # Add content to the PDF
    data = [
        f"Student Name: {student_name}",
        f"Address: {student_address}",
        f"Gender: {student_gender}",
        f"Roll Number: {student_roll_number}",
        f"Room Number: {student_room_number}",
        f"Phone Number: {student_phone_number}",
        "",  # Empty row for spacing
        ["Month", "Year", "Days of Leave Taken", "Total Days in Month", "Amount Due", "Payment Status"]
    ]
    bills = Billing.objects.filter(student=student)
    for bill in bills:
        data.append([
            bill.month,
            bill.year,
            bill.days_of_leave_taken,
            bill.total_days_in_month,
            bill.amount_due,
            "Paid" if bill.payment_status else "Unpaid"
        ])

    table = Table(data[7:], colWidths=100, rowHeights=30)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    
    # Build elements
    watermark = Paragraph(watermark_text, watermark_style)
    elements = [watermark, title_paragraph] + [Spacer(1, 20)] + [Paragraph(item, styles['Normal']) for item in data[:6]] + [Spacer(1, 20), table]

    # Function to draw watermark on each page
    def draw_watermark(canvas, doc, watermark_text, font_size=20, x_offset=100, y_offset=-100):
        canvas.saveState()
        canvas.setFont('Helvetica', font_size)  # Adjust font size as needed
        canvas.setFillAlpha(0.3)  # Set opacity to 0.3
        canvas.rotate(45)
        canvas.drawString(x_offset, y_offset, watermark_text)
        canvas.restoreState()

    # Add watermark to every page
    doc.build(elements, onFirstPage=lambda canvas, doc: draw_watermark(canvas, doc, watermark_text, font_size=70, x_offset=200, y_offset=800), onLaterPages=lambda canvas, doc: draw_watermark(canvas, doc, watermark_text, font_size=30, x_offset=150, y_offset=800))

    # Return PDF data
    return buffer.getvalue()





def view_bills(request):
    student = Student.objects.get(user=request.user)
    bills = Billing.objects.filter(student=student)
    return render(request, 'student/view_bills.html', {'bills': bills})

def view_bills_as_pdf(request):
    student = Student.objects.get(user=request.user)
    pdf_data = generate_bills_pdf(student)

    # Create HTTP response with PDF as attachment
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bills.pdf"'
    response.write(pdf_data)
    return response
