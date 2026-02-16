from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from django.apps import apps
from datetime import timedelta, datetime
from decimal import Decimal
import json


def get_model_class(model_name):
    """
    Retourne la classe du modèle à partir de son nom.
    Utilise l'auto-découverte Django pour trouver le modèle.
    """
    # Parcourir toutes les apps pour trouver le modèle
    for app_config in apps.get_app_configs():
        try:
            model = app_config.get_model(model_name)
            if model:
                return model
        except LookupError:
            # Le modèle n'existe pas dans cette app, continuer
            continue
    
    # Si le modèle n'est pas trouvé, essayer avec le nom complet app.ModelName
    if '.' in model_name:
        try:
            app_label, model_name_only = model_name.split('.', 1)
            app_config = apps.get_app_config(app_label)
            return app_config.get_model(model_name_only)
        except (LookupError, ValueError):
            pass
    
    return None


@require_http_methods(["GET"])
def chart_data(request):
    """API pour récupérer les données de graphique"""
    model_name = request.GET.get('model')
    field_name = request.GET.get('field')
    chart_type = request.GET.get('type', 'line')
    frequency = request.GET.get('frequency', 'month')
    operation = request.GET.get('operation', 'sum')
    
    if not model_name or not field_name:
        return JsonResponse({'error': 'Model and field are required'}, status=400)
    
    model_class = get_model_class(model_name)
    if not model_class:
        return JsonResponse({'error': 'Invalid model'}, status=400)
    
    # Vérifier que le champ existe
    try:
        # Créer une instance pour vérifier les champs
        instance = model_class()
        if not hasattr(instance, field_name):
            # Liste des champs disponibles
            available_fields = [f.name for f in model_class._meta.get_fields() if hasattr(f, 'name')]
            numeric_fields = []
            for field in model_class._meta.get_fields():
                if hasattr(field, 'name'):
                    field_obj = model_class._meta.get_field(field.name)
                    if hasattr(field_obj, 'get_internal_type'):
                        field_type = field_obj.get_internal_type()
                        if field_type in ['DecimalField', 'FloatField', 'IntegerField', 'PositiveIntegerField', 'BigIntegerField']:
                            numeric_fields.append(field.name)
            
            return JsonResponse({
                'error': f'Le champ "{field_name}" n\'existe pas sur le modèle {model_name}',
                'available_fields': numeric_fields,
                'suggestion': numeric_fields[0] if numeric_fields else None
            }, status=400)
    except Exception as e:
        return JsonResponse({'error': f'Erreur lors de la vérification du champ: {str(e)}'}, status=400)
    
    # Calculer la période selon la fréquence
    now = timezone.now()
    periods_map = {
        'day': 30,
        'week': 12,
        'month': 12,
        'quarter': 8,
        'year': 5,
    }
    periods = periods_map.get(frequency, 12)
    
    # Récupérer les données
    data = []
    labels = []
    
    for i in range(periods - 1, -1, -1):
        if frequency == 'day':
            start = now - timedelta(days=i+1)
            end = now - timedelta(days=i)
            label = start.strftime('%d/%m')
        elif frequency == 'week':
            start = now - timedelta(weeks=i+1)
            end = now - timedelta(weeks=i)
            label = f"Sem {start.isocalendar()[1]}"
        elif frequency == 'month':
            # Calculer le début du mois
            month_start = now.month - i - 1
            year = now.year
            while month_start < 1:
                month_start += 12
                year -= 1
            start = timezone.make_aware(datetime(year, month_start, 1))
            month_end = now.month - i
            year_end = now.year
            while month_end < 1:
                month_end += 12
                year_end -= 1
            end = timezone.make_aware(datetime(year_end, month_end, 1))
            label = start.strftime('%m/%Y')
        elif frequency == 'quarter':
            quarter = ((now.month - 1) // 3) - i
            year = now.year
            while quarter < 0:
                quarter += 4
                year -= 1
            month_start = (quarter * 3) + 1
            start = timezone.make_aware(datetime(year, month_start, 1))
            label = f"T{quarter + 1} {year}"
            end = start + timedelta(days=90)
        else:  # year
            year = now.year - i
            start = timezone.make_aware(datetime(year, 1, 1))
            end = timezone.make_aware(datetime(year + 1, 1, 1))
            label = str(year)
        
        # Filtrer les données pour cette période
        queryset = model_class.objects.filter(created_at__gte=start, created_at__lt=end)
        
        # Appliquer l'opération
        if operation == 'sum':
            try:
                from django.db.models import Sum
                result = queryset.aggregate(sum=Sum(field_name))
                value = float(result['sum'] or 0)
            except:
                value = 0
        elif operation == 'avg':
            try:
                from django.db.models import Avg
                result = queryset.aggregate(avg=Avg(field_name))
                value = float(result['avg'] or 0)
            except:
                value = 0
        elif operation == 'count':
            value = queryset.count()
        else:
            value = queryset.count()
        
        data.append(value)
        labels.append(label)
    
    return JsonResponse({
        'labels': labels,
        'data': data,
        'chart_type': chart_type
    })


@require_http_methods(["GET"])
def grid_data(request):
    """API pour récupérer les données de grille"""
    grid_id = request.GET.get('grid_id')
    model_name = request.GET.get('model')
    columns = request.GET.getlist('columns')
    
    if not model_name:
        return JsonResponse({'error': 'Model is required'}, status=400)
    
    model_class = get_model_class(model_name)
    if not model_class:
        return JsonResponse({'error': 'Invalid model'}, status=400)
    
    # Récupérer les données
    queryset = model_class.objects.all()
    
    # Construire les données
    data = []
    for obj in queryset[:100]:  # Limiter à 100 résultats
        row = {}
        for col in columns:
            if hasattr(obj, col):
                value = getattr(obj, col)
                # Convertir les objets en string
                if hasattr(value, '__str__'):
                    row[col] = str(value)
                else:
                    row[col] = value
            else:
                row[col] = '-'
        data.append(row)
    
    return JsonResponse({
        'data': data,
        'columns': columns
    })


@require_http_methods(["GET"])
def stats_data(request):
    """API pour récupérer les statistiques rapides - utilise l'auto-découverte"""
    from django.db.models import Sum
    from django.apps import apps
    
    stats = {}
    total_revenue = 0
    
    # Parcourir tous les modèles pour détecter automatiquement ceux avec des données
    for app_config in apps.get_app_configs():
        # Ignorer les apps Django internes
        if app_config.name.startswith('django.contrib'):
            continue
        
        for model in app_config.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            
            model_name = model.__name__.lower()
            
            # Chercher des champs de montant pour calculer les revenus
            if hasattr(model, 'total_amount'):
                count = model.objects.count()
                revenue = float(model.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
                stats[model_name] = count
                total_revenue += revenue
            elif hasattr(model, 'amount'):
                count = model.objects.count()
                revenue = float(model.objects.aggregate(Sum('amount'))['amount__sum'] or 0)
                stats[model_name] = count
                total_revenue += revenue
            else:
                # Compter simplement le nombre d'objets
                count = model.objects.count()
                if count > 0:
                    stats[model_name] = count
    
    # Ajouter le revenu total
    stats['revenue'] = total_revenue
    
    # Garder la compatibilité avec l'ancien format pour l'index.html
    # On essaie de trouver les modèles courants
    order_model = get_model_class('Order')
    invoice_model = get_model_class('Invoice')
    payment_model = get_model_class('Payment')
    product_model = get_model_class('Product')
    
    result = {
        'orders': order_model.objects.count() if order_model else 0,
        'invoices': invoice_model.objects.count() if invoice_model else 0,
        'payments': payment_model.objects.count() if payment_model else 0,
        'products': product_model.objects.count() if product_model else 0,
        'revenue': total_revenue,
    }
    
    return JsonResponse(result)


@require_http_methods(["GET"])
def model_fields(request):
    """API pour récupérer les champs numériques d'un modèle - utilise l'auto-découverte"""
    model_name = request.GET.get('model')
    
    if not model_name:
        return JsonResponse({'error': 'Model name is required'}, status=400)
    
    model_class = get_model_class(model_name)
    if not model_class:
        return JsonResponse({'error': f'Model "{model_name}" not found'}, status=404)
    
    # Détecter les champs numériques
    numeric_fields = []
    for field in model_class._meta.get_fields():
        if hasattr(field, 'name'):
            try:
                field_obj = model_class._meta.get_field(field.name)
                if hasattr(field_obj, 'get_internal_type'):
                    field_type = field_obj.get_internal_type()
                    if field_type in ['DecimalField', 'FloatField', 'IntegerField', 
                                     'PositiveIntegerField', 'BigIntegerField', 'SmallIntegerField']:
                        numeric_fields.append(field.name)
            except Exception:
                # Ignorer les champs qui ne peuvent pas être inspectés
                continue
    
    return JsonResponse({
        'model': model_name,
        'fields': numeric_fields,
    })
