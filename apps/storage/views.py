from django.shortcuts import render, HttpResponse
from django.http import JsonResponse,QueryDict
from dateutil.tz import tzutc
from scripts.auth import load_k8s,self_login_auth, time_format
from kubernetes import client

@self_login_auth
def pvc(request):
    return render(request, 'storage/pvc.html')

@self_login_auth
def pvc_api(request):
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get('SearchKey')
        namespace = request.GET.get('namespace')
        try:
            for pvc in core_api.list_namespaced_persistent_volume_claim(namespace=namespace).items:
                name = pvc.metadata.name
                namespace = pvc.metadata.namespace
                labels = pvc.metadata.labels
                storage_class_name = pvc.spec.storage_class_name
                access_modes = pvc.spec.access_modes
                capacity = (pvc.status.capacity if pvc.status.capacity is None else pvc.status.capacity["storage"])
                volume_name = pvc.spec.volume_name
                status = pvc.status.phase
                create_time = time_format(pvc.metadata.creation_timestamp)

                pvc = {"name": name, "namespace": namespace, "lables": labels,
                       "storage_class_name": storage_class_name, "access_modes": access_modes, "capacity": capacity,
                       "volume_name": volume_name, "status": status, "create_time": create_time}
                if search_val:
                    if search_val in name:
                        data.append(pvc)
                else:
                    data.append(pvc)
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




@self_login_auth
def cm(request):
    return render(request, 'storage/configmap.html')

@self_login_auth
def cm_api(request):
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get('SearchKey')
        namespace = request.GET.get('namespace')
        try:
            for cm in core_api.list_namespaced_config_map(namespace=namespace).items:
                name = cm.metadata.name
                namespace = cm.metadata.namespace
                labels = cm.metadata.labels
                create_time = time_format(cm.metadata.creation_timestamp)

                cm = {"name": name, "namespace": namespace, "labels": labels, "create_time": create_time}
                if search_val:
                    if search_val in name:
                        data.append(cm)
                else:
                    data.append(cm)
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


self_login_auth
def secret(request):
    return render(request, 'storage/secret.html')

@self_login_auth
def secret_api(request):
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get('SearchKey')
        namespace = request.GET.get('namespace')
        try:
            for secret in core_api.list_namespaced_secret(namespace=namespace).items:
                name = secret.metadata.name
                namespace = secret.metadata.namespace
                labels = secret.metadata.labels
                create_time = time_format(secret.metadata.creation_timestamp)

                se = {"name": name, "namespace": namespace, "labels": labels, "create_time": create_time}
                if search_val:
                    if search_val in name:
                        data.append(secret)
                else:
                    data.append(secret)
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