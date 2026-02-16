from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
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


@staff_member_required
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
        
        # Champ date pour le filtre (compatible modèles sans created_at)
        date_field = None
        for name in ('created_at', 'date_joined', 'created', 'date_created'):
            if hasattr(model_class, name):
                try:
                    model_class._meta.get_field(name)
                    date_field = name
                    break
                except Exception:
                    pass
        if date_field:
            queryset = model_class.objects.filter(**{f'{date_field}__gte': start, f'{date_field}__lt': end})
        else:
            queryset = model_class.objects.all()
        
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


@staff_member_required
@require_http_methods(["GET"])
def grid_data(request):
    """API pour récupérer les données de grille"""
    grid_id = request.GET.get('grid_id')
    model_name = request.GET.get('model')
    columns = request.GET.getlist('columns')
    
    if not model_name:
        return JsonResponse({'error': 'Model is required'}, status=400)

    if model_name == 'User':
        from django.contrib.auth import get_user_model
        model_class = get_user_model()
    else:
        model_class = get_model_class(model_name)
    if not model_class:
        return JsonResponse({'error': 'Invalid model'}, status=400)

    queryset = model_class.objects.all()

    # Filtre optionnel : vue Clients = utilisateurs non staff (User, is_staff=false)
    if model_name == 'User' and request.GET.get('is_staff') == 'false':
        queryset = queryset.filter(is_staff=False)
        # Filtres et pagination pour Clients (logique API)
        from django.db.models import Q
        q = request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) |
                Q(email__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q)
            )
        try:
            queryset = queryset.order_by('-date_joined')
        except Exception:
            queryset = queryset.order_by('-pk')
        total_count = queryset.count()
        page = max(1, int(request.GET.get('page', 1)))
        page_size = min(100, max(1, int(request.GET.get('page_size', 20))))
        start = (page - 1) * page_size
        queryset = queryset[start:start + page_size]
    elif model_name != 'Order':
        total_count = None
    
    # Ordre explicite pour Product : plus récents en premier (liste bien ordonnée)
    if model_name == 'Product':
        try:
            ordering = queryset.model._meta.ordering or ['-created_at']
            queryset = queryset.order_by(*ordering)
        except Exception:
            queryset = queryset.order_by('-created_at') if hasattr(queryset.model, 'created_at') else queryset.order_by('name')
    
    # Filtres et pagination pour Order (logique API)
    if model_name == 'Order':
        from django.db.models import Q
        q = request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(order_number__icontains=q) |
                Q(user__username__icontains=q) |
                Q(status__icontains=q)
            )
        status_filter = request.GET.get('status', '').strip()
        if status_filter and status_filter.lower() not in ('tous', 'all', ''):
            status_map = {
                'payée': 'delivered', 'payee': 'delivered',
                'en attente': 'pending',
                'préparation': 'processing', 'preparation': 'processing',
                'expédiée': 'shipped', 'expediee': 'shipped',
                'livrée': 'delivered', 'livree': 'delivered',
                'échec': 'cancelled', 'echec': 'cancelled', 'annulée': 'cancelled',
            }
            status_value = status_map.get(status_filter.lower(), status_filter)
            queryset = queryset.filter(status=status_value)
        period = request.GET.get('period', '').strip()
        if period:
            try:
                days = int(''.join(c for c in period if c.isdigit()) or 30)
                since = timezone.now() - timedelta(days=days)
                queryset = queryset.filter(created_at__gte=since)
            except (ValueError, TypeError):
                pass
        total_count = queryset.count()
        page = max(1, int(request.GET.get('page', 1)))
        page_size = min(100, max(1, int(request.GET.get('page_size', 20))))
        start = (page - 1) * page_size
        queryset = queryset[start:start + page_size]
    elif model_name != 'User':
        total_count = None
        # Limite par défaut (Product: 200 pour une liste complète)
        limit = 200 if model_name == 'Product' else 100
        queryset = queryset[:limit]
    
    # Construire les données
    data = []
    for obj in queryset:
        row = {}
        for col in columns:
            if hasattr(obj, col):
                value = getattr(obj, col)
                if hasattr(value, '__str__'):
                    row[col] = str(value)
                else:
                    row[col] = value
            else:
                row[col] = '-'
        data.append(row)
    
    result = {'data': data, 'columns': columns}
    if total_count is not None:
        result['total_count'] = total_count
    return JsonResponse(result)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def order_create(request):
    """API pour créer une commande (logique backend)."""
    Order = get_model_class('Order')
    User = get_model_class('User')
    if not Order or not User:
        return JsonResponse({'error': 'Modèle Order ou User introuvable'}, status=400)
    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    user_id = body.get('user_id')
    if not user_id:
        return JsonResponse({'error': 'user_id requis'}, status=400)
    try:
        user = User.objects.get(pk=int(user_id))
    except (User.DoesNotExist, ValueError, TypeError):
        return JsonResponse({'error': 'Utilisateur invalide'}, status=400)
    total_amount = body.get('total_amount', 0)
    try:
        total_amount = Decimal(str(total_amount))
    except Exception:
        total_amount = Decimal('0')
    shipping_address = (body.get('shipping_address') or '').strip() or 'À renseigner'
    shipping_city = (body.get('shipping_city') or '').strip() or 'Ville'
    shipping_postal_code = (body.get('shipping_postal_code') or '').strip() or ''
    shipping_country = (body.get('shipping_country') or '').strip() or 'Pays'
    status = (body.get('status') or 'pending').strip() or 'pending'
    valid_statuses = [c[0] for c in Order.STATUS_CHOICES]
    if status not in valid_statuses:
        status = 'pending'
    notes = (body.get('notes') or '').strip() or None
    order = Order(
        user=user,
        total_amount=total_amount,
        shipping_address=shipping_address,
        shipping_city=shipping_city,
        shipping_postal_code=shipping_postal_code,
        shipping_country=shipping_country,
        status=status,
        notes=notes,
    )
    order.save()
    return JsonResponse({
        'ok': True,
        'id': order.pk,
        'order_number': order.order_number,
    }, status=201)


@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def client_create(request):
    """API pour créer un client (User avec is_staff=False)."""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    content_type = (request.content_type or '').split(';')[0].strip().lower()
    if content_type == 'application/json':
        raw = request.body
        if not raw:
            return JsonResponse({'error': 'Body vide. Envoyez un JSON avec au moins "username".'}, status=400)
        try:
            body = json.loads(raw.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
            return JsonResponse({'error': 'JSON invalide'}, status=400)
        if not isinstance(body, dict):
            body = {}
    else:
        body = {
            'username': request.POST.get('username', ''),
            'email': request.POST.get('email', ''),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'password': request.POST.get('password', ''),
        }

    username = (body.get('username') or '').strip()
    if not username:
        return JsonResponse({'error': 'username requis'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Cet identifiant existe déjà'}, status=400)
    email = (body.get('email') or '').strip()
    first_name = (body.get('first_name') or '').strip()
    last_name = (body.get('last_name') or '').strip()
    password = body.get('password') or ''
    if not password:
        password = User.objects.make_random_password(length=12)
    try:
        user = User.objects.create_user(
            username=username,
            email=email or '',
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_active=True,
        )
    except Exception as e:
        err = str(e)
        if not err:
            err = 'Erreur à la création'
        return JsonResponse({'error': err}, status=400)
    return JsonResponse({
        'ok': True,
        'id': user.pk,
        'username': user.username,
    }, status=201)


@staff_member_required
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


@staff_member_required
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
