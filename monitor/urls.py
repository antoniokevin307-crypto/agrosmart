from django.urls import path
from . import views
from . import views_auth
from . import views_admin
from . import views_moon

def ia_chat_screen(request):
    from django.contrib.auth.decorators import login_required
    from django.shortcuts import render
    return render(request, "ia_chat.html")

urlpatterns = [
    # Rutas de autenticación
    path("registro/", views_auth.register_view, name="register"),
    path("verificar-email/<str:email>/", views_auth.verify_email_view, name="verify_email"),
    path("crear-password/<str:email>/", views_auth.create_password_view, name="create_password"),
    path("iniciar-sesion/", views_auth.login_view, name="login"),
    path("cerrar-sesion/", views_auth.logout_view, name="logout"),
    path("solicitar-codigo/", views_auth.request_new_code_view, name="request_new_code"),
    path("configurar-gmail/", views_auth.setup_gmail_view, name="setup_gmail"),
    path("recuperar-cuenta/", views_auth.recover_account_view, name="recover_account"),
    
    # Rutas de administración (solo para root)
    path("admin/", views_admin.admin_panel, name="admin_panel"),
    path("admin/usuario/<int:user_id>/", views_admin.user_detail, name="user_detail"),
    path("admin/usuario/<int:user_id>/eliminar/", views_admin.delete_user, name="delete_user"),
    path("admin/cultivo/<int:crop_id>/eliminar/", views_admin.delete_crop_admin, name="delete_crop_admin"),
    path("admin/cultivo/<int:crop_id>/descargar-pdf/", views_admin.download_crop_pdf, name="download_crop_pdf"),
    path("admin/usuario/<int:user_id>/descargar-pdf/", views_admin.download_user_crops_pdf, name="download_user_crops_pdf"),
    
    # Rutas de cultivos
    path("", views.home, name="crop_list"),
    path("cultivos/nuevo/", views.crop_create, name="crop_create"),
    path("cultivos/<int:crop_id>/editar/", views.crop_edit, name="crop_edit"),
        path("cultivos/<int:crop_id>/eliminar/", views.crop_delete, name="crop_delete"),
        path("cultivos/<int:crop_id>/detalle/", views.crop_detail, name="crop_detail"),
    path("cultivos/<int:crop_id>/descargar-pdf/", views.download_crop_pdf_user, name="download_crop_pdf_user"),
    path("descargar-mis-cultivos/", views.download_my_crops_pdf, name="download_my_crops_pdf"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/<int:crop_id>/", views.dashboard, name="dashboard_crop"),
    path("api/crop/<int:crop_id>/weather/", views.get_crop_weather, name="get_crop_weather"),
    # Perfil de usuario
    path("perfil/", views.profile_view, name="profile"),
    path("perfil/editar/", views.profile_edit, name="profile_edit"),
    # Endpoint AI chat
    path("ai/chat/", views.ai_chat, name="ai_chat"),
    path("ia/", ia_chat_screen, name="ia_chat"),
    path("alerta/<int:crop_id>/respuesta/", views.alert_response, name="alert_response"),
    path("alertas/", views.alerts_list, name="alerts_list"),
    path("cultivos/<int:crop_id>/abono/", views.abono_application, name="abono_application"),
    path("abono/<int:abono_id>/<str:new_status>/", views.update_abono_status, name="update_abono_status"),
    path("cultivos/<int:crop_id>/calendario/", views.planting_calendar, name="planting_calendar"),
    path("alerta/<int:alert_id>/resolver/", views.resolve_alert, name="resolve_alert"),
    path("about/", views.about, name="about_page"),
    path("contact/", views.contact_page, name="contact_page"),
    path("luna/calendario/", views_moon.moon_calendar, name="moon_calendar"),
]
