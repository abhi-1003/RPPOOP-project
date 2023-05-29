from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import Expense,Category
from datetime import datetime
# Create your views here.
from django.contrib import messages
@login_required(login_url='/authentication/login')
def index(request):
    categories = Category.objects.all()
    expenses = Expense.objects.filter(owner=request.user)
    context = {
        'expenses':expenses
    }
    return render(request, 'expenses/index.html',context)

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
        date_str = request.POST['expense_date']
        category = request.POST['category']


        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/add_expense.html', context)
        
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/add_expense.html', context)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'expenses/add_expense.html', context)
        
        Expense.objects.create(owner=request.user, amount=amount, date=date, category=category, description=description)
        messages.success(request, 'Expense saved successfully')

        return redirect('expenses')

def expense_edit(request, id):
    categories = Category.objects.all()
    expense = Expense.objects.get(pk = id)
    context = {
        'categories':categories,
        'expense':expense,
        'values':expense,
    }
    if request.method == "GET":
        return render(request,'expenses/edit-expense.html',context)
    if request.method == "POST":
        amount = request.POST['amount']
        description = request.POST['description']
        date_str = request.POST['expense_date']
        category = request.POST['category']


        if not amount:
            messages.error(request, 'Amount is required')
            return render(request, 'expenses/edit_expense.html', context)
        
        if not description:
            messages.error(request, 'Description is required')
            return render(request, 'expenses/edit_expense.html', context)

        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format')
            return render(request, 'expenses/add_expense.html', context)
        
        expense.owner = request.user
        expense.amount = amount
        expense.date = date
        expense.category = category
        expense.description = description
        expense.save()
        messages.success(request, "Expense Updated Successfully")
        return redirect("expenses")

def delete_expense(request, id):
    expense = Expense.objects.get(pk=id)
    expense.delete()
    messages.success(request, "Expense removed")
    return redirect('expenses')