from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_or_hr_required
from .models import ShiftType
from .forms import ShiftTypeForm

@login_required
def shift_list(request):
    shifts = ShiftType.objects.all()
    return render(request, 'shifts/shift_list.html', {'shifts': shifts})

@admin_or_hr_required
def shift_create(request):
    if request.method == 'POST':
        form = ShiftTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift type created.')
            return redirect('shifts:shift_list')
    else:
        form = ShiftTypeForm()
    return render(request, 'shifts/shift_form.html', {'form': form, 'title': 'Add Shift Type'})

@admin_or_hr_required
def shift_update(request, pk):
    shift = get_object_or_404(ShiftType, pk=pk)
    if request.method == 'POST':
        form = ShiftTypeForm(request.POST, instance=shift)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift type updated.')
            return redirect('shifts:shift_list')
    else:
        form = ShiftTypeForm(instance=shift)
    return render(request, 'shifts/shift_form.html', {'form': form, 'title': 'Edit Shift Type'})

@admin_or_hr_required
def shift_delete(request, pk):
    shift = get_object_or_404(ShiftType, pk=pk)
    if request.method == 'POST':
        shift.delete()
        messages.success(request, 'Shift type deleted.')
        return redirect('shifts:shift_list')
    return render(request, 'shifts/shift_confirm_delete.html', {'shift': shift})
