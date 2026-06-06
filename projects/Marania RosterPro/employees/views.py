from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_or_hr_required
from .models import Employee, Department, Team
from .forms import EmployeeForm, DepartmentForm, TeamForm

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees})

@admin_or_hr_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee created successfully.')
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Add Employee'})

@admin_or_hr_required
def employee_update(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, 'Employee updated successfully.')
            return redirect('employees:employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form, 'title': 'Edit Employee'})

@admin_or_hr_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, 'Employee deleted successfully.')
        return redirect('employees:employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'employee': employee})

@admin_or_hr_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'employees/department_list.html', {'departments': departments})

@admin_or_hr_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created.')
            return redirect('employees:department_list')
    else:
        form = DepartmentForm()
    return render(request, 'employees/department_form.html', {'form': form})

@admin_or_hr_required
def department_update(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=dept)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated.')
            return redirect('employees:department_list')
    else:
        form = DepartmentForm(instance=dept)
    return render(request, 'employees/department_form.html', {'form': form})

@admin_or_hr_required
def department_delete(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        dept.delete()
        messages.success(request, 'Department deleted.')
        return redirect('employees:department_list')
    return render(request, 'employees/department_confirm_delete.html', {'department': dept})

@admin_or_hr_required
def team_list(request):
    teams = Team.objects.all()
    return render(request, 'employees/team_list.html', {'teams': teams})

@admin_or_hr_required
def team_create(request):
    if request.method == 'POST':
        form = TeamForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team created.')
            return redirect('employees:team_list')
    else:
        form = TeamForm()
    return render(request, 'employees/team_form.html', {'form': form})

@admin_or_hr_required
def team_update(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        form = TeamForm(request.POST, instance=team)
        if form.is_valid():
            form.save()
            messages.success(request, 'Team updated.')
            return redirect('employees:team_list')
    else:
        form = TeamForm(instance=team)
    return render(request, 'employees/team_form.html', {'form': form})

@admin_or_hr_required
def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)
    if request.method == 'POST':
        team.delete()
        messages.success(request, 'Team deleted.')
        return redirect('employees:team_list')
    return render(request, 'employees/team_confirm_delete.html', {'team': team})
