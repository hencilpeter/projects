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

@admin_or_hr_required
def leave_batch_create(request):
    config = LeaveConfiguration.get_config()
    created = 0
    errors = []
    if request.method == 'POST':
        employee_id = request.POST.get('employee')
        start_dates = request.POST.getlist('start_date')
        end_dates = request.POST.getlist('end_date')
        reasons = request.POST.getlist('reason')
        emp = get_object_or_404(Employee, pk=employee_id) if employee_id else None
        if emp:
            for i in range(len(start_dates)):
                from datetime import datetime
                try:
                    sd = datetime.strptime(start_dates[i], '%Y-%m-%d').date()
                    ed = datetime.strptime(end_dates[i], '%Y-%m-%d').date()
                    days = (ed - sd).days + 1
                    if days > config.max_leave_days_per_month:
                        errors.append(f"Row {i+1}: exceeds max {config.max_leave_days_per_month} days")
                        continue
                    LeaveRequest.objects.create(
                        employee=emp,
                        start_date=sd,
                        end_date=ed,
                        reason=reasons[i] if i < len(reasons) else '',
                        status='approved'
                    )
                    created += 1
                except (ValueError, IndexError):
                    errors.append(f"Row {i+1}: invalid date")
        if created:
            messages.success(request, f'{created} leave entr(ies) created.')
        for e in errors:
            messages.error(request, e)
        return redirect('leaves:leave_list')
    employees = Employee.objects.filter(is_active=True)
    return render(request, 'leaves/leave_batch.html', {'config': config, 'employees': employees})

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
def leave_delete(request, pk):
    leave = get_object_or_404(LeaveRequest, pk=pk)
    if request.method == 'POST':
        leave.delete()
        messages.success(request, 'Leave request deleted.')
        return redirect('leaves:leave_list')
    return render(request, 'leaves/leave_confirm_delete.html', {'leave': leave})

@admin_or_hr_required
def leave_bulk_delete(request):
    if request.method == 'POST':
        ids = request.POST.getlist('leave_ids')
        count = LeaveRequest.objects.filter(pk__in=ids).delete()[0]
        messages.success(request, f'{count} leave request(s) deleted.')
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
