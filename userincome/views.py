from django.shortcuts import render, redirect
from .models import Source, UserIncome
from django.core.paginator import Paginator
from userpreferences.models import UserPreference
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from datetime import datetime
import datetime


def search_income(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        income = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)
        data = income.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='/authentication/login')
def index(request):
    categories = Source.objects.all()
    income = UserIncome.objects.filter(owner=request.user)
    paginator = Paginator(income, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    try:
        user_preference = UserPreference.objects.get(user=request.user)
        currency = user_preference.currency
    except UserPreference.DoesNotExist:
        currency = None

    context = {
        'income': income,
        'page_obj': page_obj,
        'currency': currency
    }
    return render(request, 'income/index.html', context)



@login_required(login_url='/authentication/login')
def add_income(request):
    sources = Source.objects.all()
    context = {
        'sources': sources,
        'values': request.POST
    }
    if request.method == 'GET':
        return render(request, 'income/add_income.html', context)

    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/add_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/add_income.html', context)

        UserIncome.objects.create(owner=request.user, amount=amount, date=date,
                                  source=source, description=description)
        messages.success(request, 'Record saved successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def income_edit(request, id):
    income = UserIncome.objects.get(pk=id)
    sources = Source.objects.all()
    context = {
        'income': income,
        'values': income,
        'sources': sources
    }
    if request.method == 'GET':
        return render(request, 'income/edit_income.html', context)
    if request.method == 'POST':
        amount = request.POST['amount']

        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'income/edit_income.html', context)
        description = request.POST['description']
        date = request.POST['income_date']
        source = request.POST['source']

        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'income/edit_income.html', context)
        income.amount = amount
        income.date = date
        income.source = source
        income.description = description

        income.save()
        messages.success(request, 'Record updated successfully')

        return redirect('income')


@login_required(login_url='/authentication/login')
def delete_income(request, id):
    income = UserIncome.objects.get(pk=id)
    income.delete()
    messages.success(request, 'Record removed')
    return redirect('income')

def income_source_summary(request):
    todays_date = datetime.date.today()
    six_months_ago = todays_date - datetime.timedelta(days=30 * 6)
    incomes = UserIncome.objects.filter(owner=request.user, date__gte=six_months_ago, date__lte=todays_date)
    source_list = Source.objects.all()
    final_rep = {}

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    for source in source_list:
        total_amount = get_income_source_amount(source)
        final_rep[source.name] = total_amount

    return JsonResponse({'income_source_data': final_rep}, safe=False)


def stats_view(request):
    return render(request,'income/stats1.html')

import csv
import datetime
from django.http import HttpResponse
from fpdf import FPDF
from PIL import Image
from .models import UserIncome, Source

def export_income_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Income' + str(datetime.datetime.now()) + '.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Source', 'Date'])
    incomes = UserIncome.objects.filter(owner=request.user)

    for income in incomes:
        date_str = income.date.strftime('%Y-%m-%d')
        writer.writerow([income.amount, income.source, date_str])

    return response


def export_income_pdf(request):
    incomes = UserIncome.objects.filter(owner=request.user)

    # Create the PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Income Report', align='C')
    pdf.ln(10)

    image_path = 'userincome/image2.png'  # Replace with the actual path to your image file
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
    pdf.image(image_path, x=85, y=pdf.y + 10, w=image_width, h=image_height)
    i = 1
    for income in incomes:
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Income {}'.format(i), align='L')
        pdf.ln(5)
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Amount: {}'.format(income.amount), align='L')
        pdf.ln(5)
        pdf.cell(0, 10, 'Source: {}'.format(income.source), align='L')
        pdf.ln(5)
        pdf.cell(0, 10, 'Date: {}'.format(income.date), align='L')
        pdf.ln(10)
        i += 1

    # Get the PDF content as a byte array
    pdf_data = pdf.output(dest='S').encode('latin-1')

    # Create the HttpResponse object with the PDF contents
    response = HttpResponse(pdf_data, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=Income.pdf'

    return response