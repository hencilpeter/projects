def get_salary_expenses_breakdown(request):
    from .models import Expense
    from datetime import datetime
    from django.http import JsonResponse

    month_year = request.GET.get("month_year", "")
    try:
        parts = month_year.split("-")
        year = int(parts[0])
        month = int(parts[1])
    except (ValueError, IndexError, TypeError):
        return JsonResponse({"success": False, "error": "Invalid month format"})

    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    salary_categories = ['Employee Salary', 'Mechanic Salary']
    expenses = Expense.objects.filter(
        expense_date__gte=start,
        expense_date__lt=end,
        expense_category__in=salary_categories,
        bill_to='Company',
    ).order_by('expense_category', 'expense_date')

    breakdown = []
    for exp in expenses:
        breakdown.append({
            "expense_id": exp.expense_id,
            "expense_date": exp.expense_date.strftime("%Y-%m-%d") if exp.expense_date else "",
            "expense_category": exp.expense_category or "",
            "expense_amount": str(exp.expense_amount or 0),
            "description": exp.description or "",
            "display_comment": exp.display_comment or "",
            "vendor": exp.vendor or "",
            "payment_method": exp.payment_method or "",
            "payment_status": exp.payment_status or "",
        })

    return JsonResponse({"success": True, "data": breakdown})
PY
