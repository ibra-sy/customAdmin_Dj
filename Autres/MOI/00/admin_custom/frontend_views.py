"""
Vues pour l'interface Frontend (Admin Console SPA)
"""
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.apps import apps

from .auth_views import SESSION_INTERFACE_KEY, INTERFACE_FRONTEND, INTERFACE_CLASSIC
from .autodiscover import get_all_models_for_charts, get_all_models_for_grids


def get_custom_admin_site():
    from .admin_site import custom_admin_site
    return custom_admin_site


def _ensure_frontend_interface(request):
    """Redirige vers l'interface classique si l'utilisateur n'a pas choisi frontend."""
    if request.session.get(SESSION_INTERFACE_KEY) != INTERFACE_FRONTEND:
        return redirect('admin:index')
    return None


def _get_frontend_context(request, extra=None):
    """Retourne le contexte pour les templates frontend."""
    context = get_custom_admin_site().each_context(request)
    context['user_display'] = request.user.get_short_name() or request.user.get_username()
    context['user_initial'] = (context['user_display'][0] if context['user_display'] else 'A').upper()
    context['switch_to_classic_url'] = '/admin/switch-interface/?to=classic'
    context['switch_to_modern_url'] = '/admin/switch-interface/?to=modern'
    context['switch_to_frontend_url'] = '/admin/switch-interface/?to=frontend'
    context['current_interface'] = request.session.get(SESSION_INTERFACE_KEY, INTERFACE_CLASSIC)
    if extra:
        context.update(extra)
    return context


@staff_member_required
def frontend_dashboard(request):
    """Tableau de bord interface frontend (Admin Console)."""
    redirect_check = _ensure_frontend_interface(request)
    if redirect_check:
        return redirect_check

    # Stats - même logique que l'API stats
    from .views import get_model_class
    order_model = get_model_class('Order') or get_model_class('Commande')
    invoice_model = get_model_class('Invoice')
    payment_model = get_model_class('Payment') or get_model_class('Paiement')
    product_model = get_model_class('Product') or get_model_class('Produit')

    stats = {
        'orders': order_model.objects.count() if order_model else 0,
        'invoices': invoice_model.objects.count() if invoice_model else 0,
        'payments': payment_model.objects.count() if payment_model else 0,
        'products': product_model.objects.count() if product_model else 0,
        'revenue': 0,
    }

    total_revenue = 0
    for app_config in apps.get_app_configs():
        if app_config.name.startswith('django.contrib'):
            continue
        for model in app_config.get_models():
            if model._meta.abstract or model._meta.proxy:
                continue
            if hasattr(model, 'total_amount'):
                total_revenue += float(model.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0)
            elif hasattr(model, 'amount'):
                total_revenue += float(model.objects.aggregate(Sum('amount'))['amount__sum'] or 0)
            elif hasattr(model, 'prix_total'):
                total_revenue += float(model.objects.aggregate(Sum('prix_total'))['prix_total__sum'] or 0)
            elif hasattr(model, 'montant'):
                total_revenue += float(model.objects.aggregate(Sum('montant'))['montant__sum'] or 0)
    stats['revenue'] = total_revenue

    context = _get_frontend_context(request, {
        'title': 'Admin Console',
        'page': 'dashboard',
        'stats': stats,
        'app_list': get_custom_admin_site().get_app_list(request),
    })
    return render(request, 'admin_custom/frontend/admin_console.html', context)


@staff_member_required
def frontend_charts(request):
    """Graphiques - interface frontend."""
    redirect_check = _ensure_frontend_interface(request)
    if redirect_check:
        return redirect_check

    models = get_all_models_for_charts()
    context = _get_frontend_context(request, {
        'title': 'Graphiques',
        'page': 'charts',
        'models': models,
    })
    return render(request, 'admin_custom/frontend/charts.html', context)


@staff_member_required
def frontend_grids(request):
    """Grilles - interface frontend."""
    redirect_check = _ensure_frontend_interface(request)
    if redirect_check:
        return redirect_check

    models = get_all_models_for_grids()
    context = _get_frontend_context(request, {
        'title': 'Grilles de données',
        'page': 'grids',
        'models': models,
    })
    return render(request, 'admin_custom/frontend/grids.html', context)


@staff_member_required
def frontend_settings(request):
    """Paramètres - interface frontend."""
    redirect_check = _ensure_frontend_interface(request)
    if redirect_check:
        return redirect_check

    context = _get_frontend_context(request, {
        'title': 'Paramètres',
        'page': 'settings',
    })
    return render(request, 'admin_custom/frontend/settings.html', context)


@staff_member_required
def frontend_profile(request):
    """Profil utilisateur - interface frontend."""
    redirect_check = _ensure_frontend_interface(request)
    if redirect_check:
        return redirect_check

    context = _get_frontend_context(request, {
        'title': 'Mon profil',
        'page': 'profile',
    })
    return render(request, 'admin_custom/frontend/profile.html', context)


@staff_member_required
def frontend_notifications(request):
    """Notifications - interface frontend."""
    redirect_check = _ensure_frontend_interface(request)
    if redirect_check:
        return redirect_check

    context = _get_frontend_context(request, {
        'title': 'Notifications',
        'page': 'notifications',
    })
    return render(request, 'admin_custom/frontend/notifications.html', context)
