from django.contrib import admin
from django.urls import include, path
from store import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('components', views.components_view, name='components'),
    path('laptops', views.laptops_view, name='laptops'),
    path('login/', views.login_view, name='login'),
    path('sign_up', views.sign_up_view, name='sign_up'),
    path('log_out', views.sign_out, name='logout'),
    path('product/<int:product_id>/', views.product_view, name='product'),
    path('processors', views.processors_view, name='processors'),
    path('gpu', views.graphics_view, name='graphics'),
    path('ram', views.ram_view, name='ram'),
    path('motherboards', views.motherboards_view, name='motherboards'),
    path('storage', views.storage_view, name='storage'),
    path('power_supply', views.power_view, name='power'),
    path('cases', views.case_view, name='case'),
    path('headphones', views.headphones_view, name='headphones'),
    path('keyboards', views.keyboard_view, name='keyboards'),
    path('refrigeration', views.refrigeration_view, name='refrigeration'),
    path('monitors', views.monitor_view, name='monitor'),
    path('chairs', views.chair_view, name='chair'),
    path('accessories', views.accesory_view, name='accessory'),
    path('shopping_cart', views.cart_view, name='cart'),
    path('api/cart_item_count/', views.cart_item_count, name='cart_item_count'),
    path('remove_from_cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
      

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)