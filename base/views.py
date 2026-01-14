from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.shortcuts import render
from cars.models import Car
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View


class Home(View):
    def get(self, request, *args, **kwargs):
        cars = Car.objects.filter(is_available=True, highlighted=True).select_related('brand').order_by('-created_at')[:3]
        context = {'cars': cars}
        return render(request, 'home.html', context)

@method_decorator(staff_member_required(login_url='/usuarios/login/'), name='dispatch')
class Logs(View):
    def get(self, request, *args, **kwargs):
        logs_root = Path(getattr(settings, 'LOGS_ROOT', Path(settings.BASE_DIR) / 'logs'))
        available_dates = []

        if logs_root.exists():
            for entry in logs_root.iterdir():
                if entry.is_dir():
                    try:
                        date_obj = datetime.strptime(entry.name, '%Y-%m-%d').date()
                    except ValueError:
                        continue
                    available_dates.append(
                        {
                            'value': entry.name,
                            'label': date_obj.strftime('%d/%m/%Y'),
                        }
                    )

        available_dates.sort(key=lambda item: item['value'], reverse=True)
        available_date_values = [item['value'] for item in available_dates]

        requested_date_value = request.GET.get('log_date')
        selected_date_value = (
            requested_date_value
            if requested_date_value in available_date_values
            else (available_date_values[0] if available_date_values else None)
        )

        selected_date = None
        if selected_date_value:
            selected_date = datetime.strptime(selected_date_value, '%Y-%m-%d').date()

        selection_notice = ''
        if requested_date_value and requested_date_value not in available_date_values:
            selection_notice = f"Nenhum diretório encontrado para {requested_date_value}. "

        log_content = ''
        if selected_date_value:
            log_file = logs_root / selected_date_value / 'cars.log'
            if log_file.exists():
                log_content = log_file.read_text(encoding='utf-8', errors='replace')
                log_status_message = (
                    f"{selection_notice}Logs de {selected_date_value} carregados com sucesso."
                )
            else:
                log_status_message = (
                    f"{selection_notice}Nenhum arquivo encontrado para {selected_date_value}."
                )
        else:
            log_status_message = 'Nenhum diretório de logs encontrado.'

        context = {
            'log_content': log_content,
            'available_dates': available_dates,
            'selected_date_value': selected_date_value,
            'selected_date': selected_date,
            'log_status_message': log_status_message,
        }
        return render(request, 'logs.html', context)