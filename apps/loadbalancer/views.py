from django.shortcuts import render, HttpResponse
from django.http import JsonResponse,QueryDict
from dateutil.tz import tzutc
from scripts.auth import load_k8s,self_login_auth, time_format
from kubernetes import client

@self_login_auth
def service(request):
    return render(request, 'loadbalancer/service.html')

@self_login_auth
def service_api(request):
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get('SearchKey')
        namespace = request.GET.get('namespace')
        try:
            for svc in core_api.list_namespaced_service(namespace=namespace).items:
                name = svc.metadata.name
                namespace = svc.metadata.namespace
                labels = svc.metadata.labels
                type = svc.spec.type
                cluster_ip = svc.spec.cluster_ip
                selector = svc.spec.selector
                create_time = time_format(svc.metadata.creation_timestamp)
                ports = []
                for p in svc.spec.ports:
                    port_name = p.name
                    port = p.port
                    protocol = p.protocol
                    target_port = p.target_port
                    node_port = p.node_port
                    port = {
                        "port_name": port_name, "port": port, "protocol": protocol, "target_port": target_port, "node_port": node_port
                    }

                    ports.append(port)
                #判断是否和enpoint关联
                endpoint = ""
                for ep in core_api.list_namespaced_endpoints(namespace=namespace).items:
                    if ep.metadata.name == name and ep.subsets is None:
                        endpoint = "未关联"
                    else:
                        endpoint = "已关联"
                svc = {"name": name, "namespace": namespace, "labels": labels, "type": type, "cluster_ip": cluster_ip,
                       "selector": selector, "ports": ports, "endpoint": endpoint,
                       "create_time": create_time}
                if search_val:
                    if search_val in name:
                        data.append(svc)
                else:
                    data.append(svc)
            count = len(data)
            code = 0
            msg = "查询成功."
        except Exception as e:
            status = getattr(e, 'status')
            if status == 403:
                msg = "没有访问权限!"
            else:
                msg = "查询失败！"
            code = 1
            count = 0

        page = int(request.GET.get('page'))
        limit = int(request.GET.get('limit'))
        #分页数据
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        result = {'code': code, 'msg': msg, 'data': data, 'count': count}
        return JsonResponse(result)



#ingress接口
@self_login_auth
def ingress(request):
    return render(request, 'loadbalancer/ingress.html')

@self_login_auth
def ingress_api(request):
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    network_api = client.NetworkingV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get('SearchKey')
        namespace = request.GET.get('namespace')
        try:
            for ingress in network_api.list_namespaced_ingress(namespace=namespace).items:
                name = ingress.metadata.name
                namespace = ingress.metadata.namespace
                labels = ingress.metadata.labels
                create_time = time_format(ingress.metadata.creation_timestamp)
                http_status = []
                for http in ingress.spec.rules:
                    http_host = http.host
                    paths = []
                    for pa in http.http.paths:
                        service_name = pa.backend.service.name
                        service_port = pa.backend.service.port.name or pa.backend.service.port.number
                        path = pa.path
                        path_type = pa.path_type
                        p = {"service_name": service_name, "service_port": service_port, "path": path, "path_type": path_type}
                        paths.append(p)

                    http = {'http_host': http_host, "paths": paths}
                http_status.append(http)

                ingress = {
                    "name": name,
                    "namespace": namespace,
                    "labels": labels,
                    "http_status": http_status,
                    "create_time": create_time
}
                if search_val:
                    if search_val in name:
                        data.append(ingress)
                else:
                    data.append(ingress)
            count = len(data)
            code = 0
            msg = "查询成功."
        except Exception as e:
            status = getattr(e, 'status')
            if status == 403:
                msg = "没有访问权限!"
            else:
                msg = "查询失败！"
            code = 1
            count = 0

        page = int(request.GET.get('page'))
        limit = int(request.GET.get('limit'))
        #分页数据
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        result = {'code': code, 'msg': msg, 'data': data, 'count': count}
        return JsonResponse(result)