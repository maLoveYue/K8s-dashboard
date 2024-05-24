from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from django.urls import re_path,path
from K8sManagementPlatform.consumers import StreamConsumer


application = ProtocolTypeRouter({
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                re_path(r'^workload/terminal/(?P<namespace>.*)/(?P<pod_name>.*)/(?P<container>.*)/', StreamConsumer),
            ])
        )
    ),
})




