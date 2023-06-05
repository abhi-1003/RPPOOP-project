from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Expense, Category
from django.core.paginator import Paginator
from datetime import datetime
import datetime
# Create your views here.
from django.http import JsonResponse,HttpResponse
from django.contrib import messages
import json
from django.http import JsonResponse
from userpreferences.models import UserPreference
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
# from io import BytesIO
# from pdfdocument.document import PDFDocument
import csv
# from django.template.loader import render_to_string
# from weasyprint import HTML
# import tempfile
from django.db.models import Sum
def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)
        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except ObjectDoesNotExist:
        currency = "USD"  
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # Fixed line
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='/authentication/login')
def add_expense(request):
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'expenses/add_expense.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expense.html', context)

        # try:
        #     date = datetime.strptime(date_str, '%Y-%m-%d').date()
        # except ValueError:
        #     messages.error(request, 'Invalid date format')
        #     return render(request, 'expenses/add_expense.html', context)

        Expense.objects.create(
            owner=request.user,
            amount=amount,
            date=date,
            category=category,
            description=description
        )
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')
    
@login_required(login_url='/authentication/login')
def expense_edit(request, id):
    categories = Category.objects.all()
    expense = Expense.objects.get(pk=id)
    context = {
        'categories': categories,
        'expense': expense,
        'values': expense,
    }
    if request.method == "GET":
        return render(request, 'expenses/edit-expense.html', context)  # Fixed template name
    if request.method == "POST":
        # Rest of the code...

        amount = request.POST['amount']
        description = request.POST['description']
        date = request.POST['expense_date']
        category = request.POST['category']


        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit_expense.html', context)
        
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/edit_expense.html', context)

        # try:
        #     date = request.POST['expense_date']
        # except ValueError:
        #     messages.error(request, 'Invalid date format')
        #     return render(request, 'expenses/add_expense.html', context)
        
        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()
        messages.success(request, "Expense Updated Successfully")
        return redirect("expenses")

@login_required(login_url='/authentication/login')
def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense removed")
    return redirect('expenses')

def counting(request):
    travel = Expense.objects.filter(Category='Travel').count()
    travel = int(travel)

    restaurants = Expense.objects.filter(Category='Restaurants').count()
    restaurants = int(restaurants)

    stationary = Expense.objects.filter(Category='Stationary').count()
    stationary = int(stationary)

    bills = Expense.objects.filter(Category='Bills').count()
    bills = int(bills)

    categories = [travel, restaurants, stationary, bills]
    context = {'categories':categories,'category_list':['Travel','Restaurants','Stationary','Bills']}
    return render(request,'expenses/stats.html',context)


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    category_list = Category.objects.all()
    final_rep = {}
    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount
    for category in category_list:
        total_amount = get_expense_category_amount(category)
        print(total_amount)
        final_rep[category.name] = total_amount

    return JsonResponse({'expense_category_data': final_rep}, safe=False)

# def expense_category_summary(request):
#     todays_date = datetime.date.today()
#     six_months_ago = todays_date-datetime.timedelta(days=30*6)
#     expenses = Expense.objects.filter(owner=request.user,
#                                       date__gte=six_months_ago, date__lte=todays_date)
#     finalrep = {}

#     def get_category(expense):
#         return expense.category
#     category_list = list(set(map(get_category, expenses)))

#     def get_expense_category_amount(category):
#         amount = 0
#         filtered_by_category = expenses.filter(category=category)

#         for item in filtered_by_category:
#             amount += item.amount
#         return amount

#     for x in expenses:
#         for y in category_list:
#             finalrep[y] = get_expense_category_amount(y)

#     return JsonResponse({'expense_category_data': finalrep}, safe=False)

def stats_view(request):
    return render(request,'expenses/stats.html')



def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses = Expense.objects.filter(owner=request.user)
    total = expenses.aggregate(Sum('amount'))

    for expense in expenses: 
        date_str = expense.date.strftime('%Y-%m-%d')
        writer.writerow([expense.amount, expense.description, expense.category, date_str])

    writer.writerow(['Total',total['amount__sum'],'',''])
    return response

from fpdf import FPDF
from PIL import Image
def export_pdf(request):
    expenses = Expense.objects.filter(owner=request.user)
    total = expenses.aggregate(Sum('amount'))

    # Create the PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Expense Report', align='C')
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, 'Total: {}'.format(total['amount__sum']), align='L')
    pdf.ln(10)

    image_path = 'image1.png'  # Replace with the actual path to your image file
    image = Image.open(image_path)
    image_width, image_height = image.size
    max_image_width = 40  # Define the maximum width for the image
    max_image_height = 40
    if image_width > max_image_width:
        image_height = max_image_height
        # image_height = int((max_image_width / float(image_width)) * image_height)
        image_width = max_image_width
    image = image.resize((image_width, image_height), Image.ANTIALIAS)

    # Add the image to the PDF
    pdf.image(image_path, x=85, y=pdf.y+200, w=image_width, h=image_height)
    for expense in expenses:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Expense {}'.format(expense.id), align='L')
        pdf.ln(5)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Amount: {}'.format(expense.amount), align='L')
        pdf.ln(5)
        pdf.cell(0, 10, 'Description: {}'.format(expense.description), align='L')
        pdf.ln(5)
        pdf.cell(0, 10, 'Category: {}'.format(expense.category), align='L')
        pdf.ln(5)
        pdf.cell(0, 10, 'Date: {}'.format(expense.date), align='L')
        pdf.ln(10)

    # Get the PDF content as a byte array
    pdf_data = pdf.output(dest='S').encode('latin-1')

    # Create the HttpResponse object with the PDF contents
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Expenses.pdf'

    return response
        # Read the temporary file contents


# def export_pdf(request):
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.pdf'
#     response['Content-Transfer-Encoding'] = 'binary'
#     expenses = Expense.objects.filter(owner=request.user)
#     total = expenses.aggregate(Sum('amount'))

#     pdf = PDFDocument(response)
#     pdf.init_report()
#     pdf.h1('Expense Report')
#     pdf.p('Total: {}'.format(total['amount__sum']))
#     pdf.nl(2)

#     for expense in expenses:
#         pdf.h2('Expense {}'.format(expense.id))
#         pdf.p('Amount: {}'.format(expense.amount))
#         pdf.p('Description: {}'.format(expense.description))
#         pdf.p('Category: {}'.format(expense.category))
#         pdf.p('Date: {}'.format(expense.date))
#         pdf.nl(2)

#     pdf.generate()

#     return response
# def export_pdf(request):
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.pdf'
#     response['Content-Transfer-Encoding']='binary'
#     expenses = Expense.objects.filter(owner=request.user)   
#     sum = expenses.aaggregate(Sum('amount'))
#     html_string=render_to_string('expenses /pdf-output.html',{'expenses':expenses,'total':sum})\
    

#     html=HTML(string=html_string)
#     result=html.write_pdf()
#     with tempfile.NamedTemporaryFile(delete= True) as output:
#         output.write(result)
#         output.flush()
#         output=open(output.name,'rb')
#         response.write(output.read())
#     return response    

