from django.urls import path

from . import views

urlpatterns = [
    path('run/<int:user_id>/<int:device_id>', views.run_command, name='run'),
    path('update_firmware/<int:user_id>/<int:device_id>', views.update_firmware, name='update_firmware'),

    # for debug only
    path('create_user/<slug:name>', views.create_user, name='create_user'),
    path('create_device/<int:owner_id>', views.create_device, name='create_device')
    # path('get/<int:user_id>/<int:device_id>', views.get_device, name='get'),
]