from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include("api.urls")),
]

# Una ruta que no existe o un fallo inesperado también responden en JSON.
handler404 = "api.errores.ruta_no_encontrada"
handler500 = "api.errores.error_del_servidor"
