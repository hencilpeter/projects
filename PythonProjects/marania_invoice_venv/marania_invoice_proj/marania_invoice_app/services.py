import csv, json,io
from django.http import HttpResponse
from django.db import transaction
from .serializers import MODEL_REGISTRY


@transaction.atomic
def export_data(model_name, file_type):
    model = MODEL_REGISTRY[model_name]
    queryset = model.objects.all()
    fields = [f.name for f in model._meta.fields]

    if file_type == "csv":
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{model_name}.csv"'

        writer = csv.writer(response)
        writer.writerow(fields)

        for obj in queryset:
            writer.writerow([getattr(obj, f) for f in fields])

        return response

    if file_type == "json":
        data = []
        for obj in queryset:
            record = {f: getattr(obj, f) for f in fields}
            data.append(record)

        response = HttpResponse(
            json.dumps(data, indent=2, default=str),
            content_type="application/json"
        )
        response["Content-Disposition"] = f'attachment; filename="{model_name}.json"'
        return response


@transaction.atomic
def import_data(model_name, file, file_type):
    model = MODEL_REGISTRY[model_name]
    fields = [f.name for f in model._meta.fields]

    if file_type == "csv":
        decoded = file.read().decode("utf-8")
        reader = csv.DictReader(io.StringIO(decoded))

        for row in reader:
            clean = {k: v if v != "" else None for k, v in row.items()}
            model.objects.update_or_create(**clean)

    elif file_type == "json":
        records = json.load(file)
        for record in records:
            model.objects.update_or_create(**record)