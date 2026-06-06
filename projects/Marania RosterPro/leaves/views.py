from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_or_hr_required
from employees.models import Employee
from .models import LeaveRequest, LeaveConfiguration
from .forms import LeaveRequestForm, LeaveConfigForm

@login_required
def leave_list(request):
    leaves = LeaveRequest.objects.all()
    return render(request, 'leaves/leave_list.html', {'leaves': leaves})

@login_required
def leave_create(request):
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            emp = form.cleaned_data.get('employee')
            if not emp:
                emp = Employee.objects.filter(user=request.user).first()
            if not emp:
                messages.error(request, 'Select an employee or link your account to an employee profile.')
                return render(request, 'leaves/leave_form.html', {'form': form})
            leave.employee = emp
            config = LeaveConfiguration.get_config()
            if leave.leave_days > config.max_leave_days_per_month:
                messages.error(request, f'Leave cannot exceed {config.max_leave_days_per_month} days per month.')
                return render(request, 'leaves/leave_form.html', {'form': form})
            leave.save()
            messages.success(request, 'Leave request submitted.')
            return redirect('leaves:leave_list')
    else:
        form = LeaveRequestForm()
    return render(request, 'leaves/leave_form.html', {'form': form, 'title': 'Apply for Leave'})

@admin_or_hr_required
def leave_approve(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = 'approved'
    leave.approved_by = request.user
    leave.save()
    messages.success(request, 'Leave approved.')
    return redirect('leaves:leave_list')

@admin_or_hr_required
def leave_reject(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    leave.status = 'rejected'
    leave.approved_by = request.user
    leave.save()
    messages.success(request, 'Leave rejected.')
    return redirect('leaves:leave_list')

@admin_or_hr_required
def leave_config(request):
    config = LeaveConfiguration.get_config()
    if request.method == 'POST':
        form = LeaveConfigForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Leave configuration updated.')
            return redirect('leaves:leave_config')
    else:
        form = LeaveConfigForm(instance=config)
    return render(request, 'leaves/leave_config.html', {'form': form})
