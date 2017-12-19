from sanic import Blueprint
import asyncio
import datetime
import aiomysql
from sanic import Sanic
from sanic import response
from sanic.response import json
from db_support import db_select, db_insert, db_delete, db_update, alchemyencoder
from db_support import aio_post, aio_delete, aio_put, aio_patch
import db
import os
import aiofiles
import uuid
import xlrd
import hashlib
import aiohttp
from sanic.response import stream, text
import zipfile
import json as innerjson
import time
import signal
from log_support import do_log
from config import *

bp_admin_main = Blueprint('bp_admin_main')

#ADMIN

###################################FLAVOR#############################################################################3
@bp_admin_main.get("/admin/flavor")
async def get_flavor(request):

    return_info = await db_select("flavorView")
    do_log(2, "get_flavor:查询成功![admin]")
    return json({'state': 0, 'flavor': return_info})


@bp_admin_main.post("/admin/flavor")
async def add_flavor(request):
    try:
        data = request.json
    except:
        do_log(4, "add_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_insert("flavor", created_at = time, updated_at = time, name = data['name'], author = int(data['author']), ram = int(data['ram']), cpu = int(data['cpu'])):
            do_log(2, "add_flavor:配置添加成功！[name=%s]" % (data['name'],))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "add_flavor:数据库操作失败[name=%s]" % (data['name'],))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "add_flavor:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_main.route("/admin/flavor", methods=['PATCH'])
async def update_flavor(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_flavor:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("flavor",set={ "updated_at":time, "name":data['name'], "author":int(data['author']), "ram":int(data['ram']), "cpu":int(data['cpu'])}, id=id):
            do_log(2, "update_flavor:配置修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_flavor:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "add_flavor:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_main.route("/admin/flavor/del", methods=['GET'])
async def delete_flavor(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_flavor:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_delete("flavor", id=id):
        do_log(2, "delete_flavor:配置删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "delete_flavor:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})

##########################################IMAGE########################################################################
@bp_admin_main.get("/admin/image")
async def get_image(request):
    """
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_image:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    return_info = await db_select("image", find = ['name', 'author', 'container_format', 'disk_format'], id = id )
    """
    return_info = await db_select("imageView")
    do_log(2, "get_image:镜像查询成功![admin]")
    return json({'state': 0, 'image': return_info})


@bp_admin_main.post("/admin/image")
async def add_image(request):
    try:
        data = request.json
    except:
        do_log(4, "add_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #try:
    if await db_insert("image", created_at = time, updated_at = time, name = data['name'], author = int(data['author']), resource_path = data['resource_path'], container_format = data['container_format'], disk_format = data['disk_format']):
        do_log(2, "add_image:镜像添加成功！[name=%s]" % (data['name'],))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "add_image:数据库操作失败[name=%s]" % (data['name'],))
        return json({'state': -2, 'info': '数据库操作失败'})
    #except Exception as e:
    #   #print(e)
    #   do_log(4, "add_image:参数缺失或不规范")
    #   return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_main.route("/admin/image", methods=['PATCH'])
async def update_image(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_image:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("image",set={ "updated_at":time, "name":data['name'], "author":int(data['author']), "resource_path":data['resource_path'], "container_format":data['container_format'], "disk_format":data['disk_format'],}, id=id):
            do_log(2, "update_image:镜像修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_image:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_image:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_admin_main.route("/admin/image/del", methods=['GET'])
async def delete_image(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_image:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_delete("image", id=id):
        do_log(2, "delete_image:镜像删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "delete_image:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})

############################################SOFTWARE##################################################################

@bp_admin_main.get("/admin/software")
async def get_software(request):
    """
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    return_info = await db_select("software", find = ['name', 'resource_path', 'description', 'author', 'is_public'], id = id )
    """
    return_info = await db_select("softwareView")
    do_log(2, "get_software:软件查询成功![admin]")
    return json({'state': 0, 'software': return_info})


@bp_admin_main.post("/admin/software")
async def add_software(request):
    try:
        data = request.json
    except:
        do_log(4, "add_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_insert("software", created_at = time, updated_at = time, name = data['name'], resource_path = data['resource_path'], description = data['description'], author = int(data['author']), is_public = int(data['is_public'])):
            do_log(2, "add_software:添加成功！[name=%s]" % (data['name'],))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "add_software:数据库操作失败[name=%s]" % (data['name'],))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "add_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_admin_main.route("/admin/software", methods=['PATCH'])
async def update_software(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("software",set={ "updated_at":time, "name":data['name'], "resource_path":data['resource_path'], "description":data['description'], "author":int(data['author']), "is_public":int(data['is_public'])}, id=id):
            do_log(2, "update_software:修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_software:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_admin_main.route("/admin/software/del", methods=['GET'])
async def delete_software(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_delete("software", id=id):
        do_log(2, "delete_software:删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "delete_software:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})