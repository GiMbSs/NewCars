import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.utils.functional import SimpleLazyObject
from django.conf import settings
from pathlib import Path
from .models import Car
from datetime import datetime
from ai_api.client import get_ai_description

UserModel = get_user_model()
logger = logging.getLogger('app')


def _get_actor(instance):
    """Retorna uma representação legível do usuário que executou a ação."""
    user = getattr(instance, '_log_user', None)
    if isinstance(user, (UserModel, SimpleLazyObject)) and getattr(user, 'is_authenticated', False):
        display_name = user.get_full_name() or user.get_username()
        return f"{display_name} (ID {user.pk})"
    return 'Sistema'


def _save_log(actor: str, action: str, instance) -> None:
    """Grava log de ação tanto no logger padrão quanto no arquivo diário."""
    log_message = f"{action} by {actor}: {instance}"
    logger.info(log_message)

    # Manter log diário em arquivo para a view de logs existente
    try:
        logs_root = Path(getattr(settings, 'LOGS_ROOT', Path(settings.BASE_DIR) / 'logs'))
        date_path = logs_root / str(datetime.now().date())
        date_path.mkdir(parents=True, exist_ok=True)

        log_file = date_path / 'cars.log'
        with log_file.open('a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            f.write(f"[{timestamp}] {log_message}\n")
    except Exception as e:
        logger.error('Erro ao salvar log em arquivo: %s', e)


@receiver(pre_save, sender=Car)
def before_car_save(sender, instance, **kwargs):
    if kwargs.get('raw', False):
        return  # evita rodar durante loaddata/fixtures

    actor = _get_actor(instance)

    if not instance.description:
        # evita chamar AI quando brand for objeto preguiçoso; ajuste conforme seu client
        instance.description = get_ai_description(instance.model, instance.brand.name, instance.model_year)

    if instance.pk:
        car_before = Car.objects.filter(pk=instance.pk).first()
        if car_before:
            changes = []
            fields_to_check = [
                ('model', 'Modelo'),
                ('brand', 'Marca'),
                ('factory_year', 'Ano de Fabricação'),
                ('model_year', 'Ano do Modelo'),
                ('price', 'Preço'),
                ('color', 'Cor'),
                ('transmission', 'Câmbio'),
                ('mileage', 'Quilometragem'),
                ('is_available', 'Disponível'),
                ('is_new', 'Novo'),
                ('highlighted', 'Destaque'),
                ('description', 'Descrição'),
            ]
            for field_name, field_label in fields_to_check:
                old_value = getattr(car_before, field_name, None)
                new_value = getattr(instance, field_name, None)
                if old_value != new_value:
                    changes.append(f"{field_label}: '{old_value}' → '{new_value}'")
            if changes:
                changes_str = "; ".join(changes)
                _save_log(actor, "Um carro foi atualizado", f'{car_before.model} (ID {instance.pk}) - Alterações: {changes_str}')

@receiver(post_save, sender=Car)
def after_car_save(sender, instance, created, **kwargs):
    if kwargs.get('raw', False):
        return
    actor = _get_actor(instance)
    if created:
        _save_log(actor, "Novo carro cadastrado", instance)
    else:
        _save_log(actor, "Carro atualizado", instance)

@receiver(post_delete, sender=Car)
def after_car_delete(sender, instance, **kwargs):
    if kwargs.get('raw', False):
        return
    actor = _get_actor(instance)
    _save_log(actor, "Carro deletado", instance)