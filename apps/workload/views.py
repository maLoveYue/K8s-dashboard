from django.shortcuts import render
from django.http import JsonResponse
from scripts.auth import load_k8s, self_login_auth, time_format
from kubernetes import client


@self_login_auth
def deployment(request):
    return render(request, 'workload/deployment.html')

@self_login_auth
def deployment_create(request):
    return render(request, 'workload/deploy_create.html')

@self_login_auth
def deployment_api(request):
    auth_type = request.session.get('auth_type')
    token = request.session.get('token')
    load_k8s(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == 'GET':
        data = []
        search_val = request.GET.get("SearchKey")
        namespace = request.GET.get("namespace")
        try:
            for dp in apps_api.list_namespaced_deployment(namespace).items:
                name = dp.metadata.name
                namespace = dp.metadata.namespace
                replicas = dp.spec.replicas
                available_replicas = dp.status.available_replicas
                selector = dp.spec.selector.match_labels
                create_time = time_format(dp.metadata.creation_timestamp)
                if len(dp.spec.template.spec.containers) > 1:
                    images = ""
                    n = 1
                    for c in dp.spec.template.spec.containers:
                        status = ("运行中" if dp.status.conditions[0].status == "True" else "异常")
                        image = c.image
                        images += "[%s]: %s / %s " % (n, image, status)
                        n += 1
                else:
                    status = (
                        "运行中" if dp.status.conditions[0].status == "True" else "异常")
                    image = dp.spec.template.spec.containers[0].image
                    images = "%s / %s" % (image, status)
                dp = {"name": name, "namespace": namespace, "replicas": replicas,
                      "available_replicas": available_replicas, "selector": selector,
                      "images": images, "create_time": create_time
                      }
                if search_val:
                    if search_val in name:
                        data.append(dp)
                else:
                    data.append(dp)

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


@self_login_auth
def statefulset(request):
    return render(request, 'workload/statefulset.html')


@self_login_auth
def statefulset_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    load_k8s(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == "GET":
        search_key = request.GET.get("SearchKey")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for sts in apps_api.list_namespaced_stateful_set(namespace).items:
                name = sts.metadata.name
                namespace = sts.metadata.namespace
                labels = sts.metadata.labels
                selector = sts.spec.selector.match_labels
                replicas = sts.spec.replicas
                ready_replicas = ("0" if sts.status.ready_replicas is None else sts.status.ready_replicas)
                service_name = sts.spec.service_name
                containers = {}
                for c in sts.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = time_format(sts.metadata.creation_timestamp)

                sts = {"name": name, "namespace": namespace, "labels": labels, "replicas": replicas,
                       "ready_replicas": ready_replicas, "service_name": service_name,
                       "selector": selector, "containers": containers, "create_time": create_time}

                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(sts)
                else:
                    data.append(sts)
                code = 0
                msg = "获取数据成功"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"
        count = len(data)

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        return JsonResponse(res)



@self_login_auth
def daemonset(request):
    return render(request, 'workload/daemonset.html')

@self_login_auth
def daemonset_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    load_k8s(auth_type, token)
    apps_api = client.AppsV1Api()
    if request.method == "GET":
        search_key = request.GET.get("SearchKey")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for ds in apps_api.list_namespaced_daemon_set(namespace).items:
                name = ds.metadata.name
                namespace = ds.metadata.namespace
                desired_number = ds.status.desired_number_scheduled
                available_number = ds.status.number_available
                selector = ds.spec.selector.match_labels
                containers = {}
                for c in ds.spec.template.spec.containers:
                    containers[c.name] = c.image
                create_time = time_format(ds.metadata.creation_timestamp)

                ds = {"name": name, "namespace": namespace,  "desired_number": desired_number,
                      "available_number": available_number,
                      "selector": selector, "containers": containers, "create_time": create_time}

                # 根据搜索值返回数据
                if search_key:
                    if search_key in name:
                        data.append(ds)
                else:
                    data.append(ds)
                code = 0
                msg = "获取数据成功"
        except Exception as e:
            code = 1
            status = getattr(e, "status")
            if status == 403:
                msg = "没有访问权限"
            else:
                msg = "获取数据失败"
        count = len(data)

        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit'))
        start = (page - 1) * limit
        end = page * limit
        data = data[start:end]

        res = {'code': code, 'msg': msg, 'count': count, 'data': data}
        return JsonResponse(res)

@self_login_auth
def pod(request):
    return render(request, 'workload/pod.html')


@self_login_auth
def pod_api(request):
    code = 0
    msg = ""
    auth_type = request.session.get("auth_type")
    token = request.session.get("token")
    load_k8s(auth_type, token)
    core_api = client.CoreV1Api()
    if request.method == 'GET':
        search_key = request.GET.get("SearchKey")
        namespace = request.GET.get("namespace")
        data = []
        try:
            for pod in core_api.list_namespaced_pod(namespace=namespace).items:
                name = pod.metadata.name
                labels = pod.metadata.labels
                namespace = pod.metadata.namespace
                pod_ip = pod.status.pod_ip
                create_time = time_format(pod.metadata.creation_timestamp)
                status = pod.status.phase
                container = []
                if pod.status.container_statuses is None:
                    status = pod.status.conditions[-1].reason
                else:
                    for c in pod.status.container_statuses:
                        c_name = c.name
                        c_image = c.image
                        restart_count = c.restart_count

                        c_status = ""
                        #获取容器的状态
                        if c.ready:
                            c_status = "running"
                        else:
                            if c.state.waiting is not None:
                                c_status = c.state.waiting.reason
                            elif c.state.terminated is not None:
                                c_status = c.state.terminated.reason
                            elif c.state.last_state.terminated is not None:
                                c_status = c.last_state.terminated.reason
                        c = {"c_name": c_name, "c_image": c_image, "restart_count": restart_count, "c_status": c_status}
                        #将多个容器信息追加到列表
                        container.append(c)

                pod = {
                    "name": name, "labels": labels, "namespace": namespace, "pod_ip": pod_ip,
                    "status": status, "container": container, "create_time": create_time
                }

                if search_key:
                    if search_key in name:
                        data.append(pod)
                else:
                    data.append(pod)
            code = 0
            msg = "查询成功"
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
        res = {"code": code, "msg": msg, "count": count, "data": data}
        return JsonResponse(res)


from django.views.decorators.clickjacking import xframe_options_exempt
@xframe_options_exempt
@self_login_auth
def terminal(request):
    namespace = request.GET.get("namespace")
    pod_name = request.GET.get("pod_name")
    containers = request.GET.get("containers").split(',')  # 返回 nginx1,nginx2，转成一个列表方便前端处理
    auth_type = request.session.get('auth_type') # 认证类型和token，用于传递到websocket，websocket根据sessionid获取token，让websocket处理连接k8s认证用
    token = request.session.get('token')
    connect = {'namespace': namespace, 'pod_name': pod_name, 'containers': containers, 'auth_type': auth_type, 'token': token}
    return render(request, 'workload/terminal.html', {'connect': connect})