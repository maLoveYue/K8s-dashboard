from django.shortcuts import render, HttpResponse
from django.http import JsonResponse,QueryDict
from dateutil.tz import tzutc
from scripts.auth import load_k8s,self_login_auth, time_format
from kubernetes import client
# Create your views here.

@self_login_auth
def namespace(request):
    return render(request, 'k8s/namespace.html')

@self_login_auth
def namespace_api(request):
    #获取已登录用户的信息，操作k8s api
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get('SearchKey')
        try:
            for ns in core_api.list_namespace().items:  # items返回一个对象，类LIST（[{命名空间属性},{命名空间属性}] ），每个元素是一个类字典（命名空间属性），操作类字典
                name = ns.metadata.name
                labels = ns.metadata.labels
                status = ns.status.phase
                create_time = time_format(ns.metadata.creation_timestamp)
                namespace = {"name": name, "labels": labels, "status": status, "create_time": create_time}
                if search_val:
                    if search_val in name:
                        data.append(namespace)
                else:
                    data.append(namespace)
            count = len(data)
            code = 0
            msg = "查询成功."
        except Exception as e:
            status = getattr(e, 'status') #status属性不存在
            if status == 403:
                msg = "没有访问权限!"
            else:
                msg = "查询失败！"
            code = 1
            count = 0

        if request.GET.get('page'):
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            #分页数据
            start = (page - 1) * limit
            end = page * limit
            data = data[start:end]

        result = {'code': code, 'msg': msg, 'data': data, 'count': count}
        return JsonResponse(result)

    elif request.method == 'POST':
        name = request.POST.get("name")
        for ns in core_api.list_namespace().items:
            if name == ns.metadata.name:
                return JsonResponse({'code': 1, 'msg': '命名空间已存在'})

        body = client.V1Namespace(
            api_version="v1",
            kind="Namespace",
            metadata=client.V1ObjectMeta(
                name=name
            )
        )
        try:
            core_api.create_namespace(body=body)
            code = 0
            msg = '创建成功'
        except Exception as e:
            status = getattr(e, 'status')
            if status == 403:
                msg = '权限不足'
            else:
                msg = '创建失败'
            code = 1
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)

    elif request.method == 'DELETE':
        request_data = QueryDict(request.body)
        namespace = request_data.get('name')
        try:
            core_api.delete_namespace(name=namespace)
            code = 0
            msg = '删除成功'
        except Exception as e:
            status = getattr(e, 'status')
            if status == 403:
                msg = "没有删除权限！"
            else:
                msg = "删除失败！"
            code = 1
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)


@self_login_auth
def node(request):
    return render(request, 'k8s/node.html')

@self_login_auth
def node_api(request):
    #获取已登录用户的信息，操作k8s api
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get('SearchKey')
        try:

            for node in core_api.list_node_with_http_info()[0].items:  # items返回一个对象，类LIST（[{命名空间属性},{命名空间属性}] ），每个元素是一个类字典（命名空间属性），操作类字典
                print(node.status.allocatable['memory'])
                name = node.metadata.name
                labels = node.metadata.labels
                schedulable = ('是' if node.spec.unschedulable is None else '否')
                status = node.status.conditions[-1].type
                create_time = time_format(node.metadata.creation_timestamp)
                cpu = f"{node.status.allocatable['cpu']} / {node.status.capacity['cpu']}"
                memory = f"{int(node.status.allocatable['memory'].strip('Ki'))/1024} / { int(node.status.capacity['memory'].strip('Ki')) /1024}"
                node = {"name": name,
                        "labels": labels,
                        "schedulable": schedulable,
                        "status": status,
                        "cpu":cpu,
                        "memory": memory,
                        "create_time": create_time
                }
                if search_val:
                    if search_val in name:
                        data.append(node)
                else:
                    data.append(node)
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

        if request.GET.get('page'):
            page = int(request.GET.get('page'))
            limit = int(request.GET.get('limit'))
            #分页数据
            start = (page - 1) * limit
            end = page * limit
            data = data[start:end]
        res = {'code': code, 'msg': msg, 'data': data, 'count': count}

        return JsonResponse(res)

@self_login_auth
def pv(request):
    return render(request, 'k8s/pv.html')

@self_login_auth
def pv_create(request):
    return render(request, 'k8s/pv-create.html')

@self_login_auth
def pv_api(request):
    # 获取已登录用户的信息，操作k8s api
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        search_val = request.GET.get("SearchKey")
        data = []
        try:
            for pv in core_api.list_persistent_volume().items:
                name = pv.metadata.name
                capacity = pv.spec.capacity["storage"].strip('Gi')
                persistent_volume_reclaim_policy = pv.spec.persistent_volume_reclaim_policy
                access_modes = pv.spec.access_modes[0]
                storage_class_name = pv.spec.storage_class_name
                if pv.spec.claim_ref:
                    claim = f"{pv.spec.claim_ref.namespace}/{pv.spec.claim_ref.name}"
                else:
                    claim = ""
                status = pv.status.phase
                create_time = time_format(pv.metadata.creation_timestamp)
                pv = {"name": name, "capacity": capacity,
                      "persistent_volume_reclaim_policy": persistent_volume_reclaim_policy,
                      "access_modes": access_modes, "storage_class_name": storage_class_name,
                      "claim": claim, "create_time": create_time, "status": status
                      }
                if search_val:
                    if search_val in name:
                        data.append(pv)
                else:
                    data.append(pv)

            code = 0
            msg = "查询成功."
        except Exception as e:
            status = getattr(e, 'status')
            if status == 403:
                msg = "没有访问权限!"
            else:
                msg = "查询失败！"
            code = 1
        count = len(data)

        page = int(request.GET.get('page'))
        limit = int(request.GET.get('limit'))
        # 分页数据
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]
        return JsonResponse({"code": code, "msg": msg, "count": count, "data": data})
    elif request.method == 'POST':
        name = request.POST.get("name", None)
        capacity = request.POST.get("capacity", None)
        access_mode = request.POST.get("access_mode", None)
        storage_type = request.POST.get("storage_type", None)
        server_ip = request.POST.get("server_ip", None)
        mount_path = request.POST.get("mount_path", None)

        body = client.V1PersistentVolume(
            api_version="v1",
            kind="PersistentVolume",
            metadata=client.V1ObjectMeta(name=name),
            spec=client.V1PersistentVolumeSpec(
                capacity={'storage': capacity},
                access_modes=[access_mode],
                nfs=client.V1NFSVolumeSource(
                    server=server_ip,
                    path="/ifs/kubernetes/%s" % mount_path
                )
            )
        )
        try:
            core_api.create_persistent_volume(body=body)
            code = 0
            msg = "创建成功"
        except Exception as e:
            status = getattr(e, 'status')
            if status == 403:
                msg = "没有创建权限!"
            else:
                msg = "创建失败！"
            code = 1
        res = {"code": code, "msg": msg}
        return JsonResponse(res)
    elif request.method == 'DELETE':
        request_data = QueryDict(request.body)
        name = request_data.get('name')
        try:
            core_api.delete_persistent_volume(name=name)
            code = 0
            msg = '删除成功'
        except Exception as e:
            status = getattr(e, 'status')
            if status == 403:
                msg = "没有删除权限!"
            else:
                msg = "删除失败！"
            code = 1
        res = {'code': code, 'msg': msg}
        return JsonResponse(res)

