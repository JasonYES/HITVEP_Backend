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

bp_openstack = Blueprint('bp_openstack')

#Monitor
@bp_openstack.get("/teacher/monitor")
async def get_userCourseOne(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        info=await db_select("userTemplate",u_id=id)
        template_id=[]
        infoX = []
        for item in info:
            #print(item['template'])
            if item['template'] == None or item['template'] == '':
                pass
            else:
                infoX.append(item)
                template_id.append(item['template'])
    except Exception as e:
        #print(e)
        do_log(4, "userTemplate:数据库访问失败")
        return json({'state': -1, 'info': 'userTemplate:数据库访问失败'})

    if template_id == []:
        return json({'state': 0, 'info': []})

    try:
        jsondata={"template_id":template_id}
        resp = await aio_patch(vmURL+'serveraction', jsondata)
        if resp['state'] != 1:
            return json({'state': -1, 'info': '虚拟机交互失败'})
        if resp['info'] == {}:
            return json({'state': 0, 'info': []})
        data = resp['info']
    except:
        do_log(4, "get_exp:虚拟机交互失败")
        return json({'state': -1, 'info': '虚拟机交互失败'})

    try:
        result = []
        for item in infoX:
            now = item['template']
            if data.get(str(now),'') == '':
                # info.pop(info.index(item))
                continue
            students =[]
            for stu in data[str(now)]:
                user= await db_select("user",id=int(stu))
                students.append(user[0])
            item['parameter'] = students
            result.append(item)
    except:
        do_log(4, "get_user:数据库错误")
        return json({'state': -1, 'info': '数据库错误'})
    do_log(4, "监控实验成功！")
    return json({'state':0,'info':result})


#创建环境
@bp_openstack.get("/exp")
async def exp_post(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        template = int(get_info['template'])
    except:
        do_log(4, "get_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        data={"user_id": id,"template_id": template}
        resp = await aio_post(vmURL+'environment', data)
        return json(resp)
    except:
        do_log(4, "get_exp:参数缺失或不规范")
        return json({'state': -1, 'info': '虚拟机交互失败'})


#关闭环境
@bp_openstack.route("/exp/del", methods=['GET'])
async def exp_post(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        template = int(get_info['template'])
    except:
        do_log(4, "get_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        resp = await aio_delete(vmURL+'environment?'+'template_id='+str(template)+'&user_id='+str(id))
        return json(resp)
    except Exception as e:
        do_log(4, "get_exp:虚拟机交互失败")
        return json({'state': -1, 'info': '虚拟机交互失败'})

#关闭环境。
@bp_openstack.route("/exp/state", methods=['PATCH'])
async def get_userCourseOne(request):
    try:
        info = request.json
        resp = await aio_put(vmURL+'serveraction', info)
        return json(resp)
    except:
        do_log(4, "get_server:OpenStack交互失败")
        return json({'state': -1, 'info': 'OpenStack交互失败'})

#开启环境。
@bp_openstack.route("/exp/state", methods=['POST'])
async def get_userCourseOne(request):
    try:
        info = request.json
        resp = await aio_post(vmURL+'serveraction', info)
        return json(resp)
    except:
        do_log(4, "get_server:OpenStack交互失败")
        return json({'state': -1, 'info': 'OpenStack交互失败'})

#获取console
@bp_openstack.route("/serveraction", methods=['PATCH'])
async def get_userCourseOne(request):
    try:
        info = request.json
        resp = await aio_patch(vmURL+'serveraction', info)
        return json(resp)
    except:
        do_log(4, "get_server:OpenStack交互失败")
        return json({'state': -1, 'info': 'OpenStack交互失败'})


#创建镜像
@bp_openstack.route("/vm", methods=['POST'])
async def exp_post(request):
    try:
        info = request.json
        resp = await aio_post(vmURL+'image', info)
        return json(resp)
    except:
        do_log(4, "get_exp:OpenStack交互失败")
        return json({'state': -1, 'info': 'OpenStack交互失败'})


@bp_openstack.route("/exp/closeAll", methods=['GET'])
async def delete_role(request):
    try:
        total = 0
        success = 0

        tids = await db_select("target", find=["template","user"], deleted=0)
        
    except Exception as e:
        do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
        return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
    try:
        data={"user_id_list": dictId}
        resp = await aio_put(vmURL+'user', data)
        if(resp['state'] != 1):
            do_log(4, "删除OpenStack后台账户失败!")
            return json({'state': -1, 'info':'删除OpenStack后台账户失败!'})
    except:
        do_log(4, "delete_user:OpenStack交互失败！")
        return json({'state': -1, 'info': 'OpenStack交互失败！'})
    do_log(2, "delete_role:批量删除成功[id=%d]" % (id,))
    return json({'state': 0, 'info': '成功'})

@bp_openstack.route("/exp/closeOld", methods=['GET'])
async def delete_role(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        total = 0
        success = 0
        tids = await db_select("target", find=["template","user"], deleted=0, user=id)
        print(tids)
        return json(tids)
    except Exception as e:
        do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
        return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
    # try:
    #     data={"user_id_list": dictId}
    #     resp = await aio_put(vmURL+'user', data)
    #     if(resp['state'] != 1):
    #         do_log(4, "删除OpenStack后台账户失败!")
    #         return json({'state': -1, 'info':'删除OpenStack后台账户失败!'})
    # except:
    #     do_log(4, "delete_user:OpenStack交互失败！")
    #     return json({'state': -1, 'info': 'OpenStack交互失败！'})
    # do_log(2, "delete_role:批量删除成功[id=%d]" % (id,))
    # return json({'state': 0, 'info': '成功'})


    # async def exp_post(request):
    #     get_info = request.raw_args
    #     try:
    #         id = int(get_info['id'])
    #         template = int(get_info['template'])
    #     except:
    #         do_log(4, "get_course:参数缺失或不规范")
    #         return json({'state': -1, 'info': '参数缺失或不规范'})
    #     try:
    #         resp = await aio_delete(vmURL+'environment?'+'template_id='+str(template)+'&user_id='+str(id))
    #         return json(resp)
    #     except Exception as e:
    #         do_log(4, "get_exp:虚拟机交互失败")
    #         return json({'state': -1, 'info': '虚拟机交互失败'})

#CHECK镜像
@bp_openstack.route("/vm/check", methods=['GET'])
async def exp_post(request):
    divide={
        "0": ["RegionOne","RegionTwo","RegionThree"],
        "1": ["RegionTwo","RegionThree"],
        "2": ["RegionOne","RegionThree"],
        "3": ["RegionThree"],
        "4": ["RegionTwo","RegionOne"],
        "5": ["RegionTwo"],
        "6": ["RegionOne"]
    }
    result=[]
    try:
        info = await db_select("courseTemplate")
        for inf in info:
            if inf['state'] == '7':
                continue
            for div in divide[inf['state']]:
                mid = innerjson.dumps(inf)
                temp = innerjson.loads(mid)
                temp["region"] = div
                result.append(temp)
        do_log(4, "get_exp:获取成功")
        return json({'state': 0, 'info': result})
    except Exception as e:
        # print(e)
        do_log(4, "get_exp:state解析错误")
        return json({'state': -1, 'info': 'state解析错误'})