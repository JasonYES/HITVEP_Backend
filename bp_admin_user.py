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

bp_admin_user = Blueprint('bp_admin_user')


@bp_admin_user.post("/admin/user")
async def add_user(request):
    try:
        data = request.json
    except:
        do_log(4, "add_soft:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        password = data['stu_number']
        md5 = hashlib.md5()
        md5.update(password.encode('utf-8'))
        password = md5.hexdigest()
        if await db_insert("user", created_at = time, updated_at = time, name = data['name'], email = data['email'], resource_path = data['resource_path'], passwd = password,stu_number = data['stu_number'], phone = data['phone']):
            u_id= await db_select("user",find=["id"],updated_at=time,created_at=time, stu_number = data['stu_number'], name = data['name'])
            #########
            do_log(2, "add_user:用户添加成功！[name=%s]" % (data['name'],))
            return json({'state': 0, 'info': '成功', 'id': u_id})
            #########
        else:
            do_log(4, "add_user:数据库操作失败[name=%s]" % (data['name'],))
            return json({'state': -2, 'info': '数据库操作失败'})
    except Exception as e:
        do_log(4, "add_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_user.get("/admin/user/fresh")
async def add_user(request):

    total = 0
    unlist = []
    try:
        users = await db_select("user")
        for user in users:
            if(user['op_user']==None or user['op_user']==''):
                total += 1
                unlist.append(user)
        do_log(2, "get_invalid:查询成功![admin]")
        return json({'state': 0, 'total': total, 'list': unlist})
    except Exception as e:
        do_log(4, "add_soft:参数缺失或不规范")
        return json({'state': -1, 'info': 'database select error.'})


@bp_admin_user.post("/admin/user/fresh")
async def add_user(request):

    total = 0
    success = 0
    userTodo = []
    try:
        users = await db_select("user")
        for user in users:
            if(user['op_user']==None or user['op_user']==''):
                userTodo.append(user)
                total += 1
        for todo in userTodo:
            httpdata={}
            resp = await aio_post(vmURL+'user?user_id='+str(todo['id']), httpdata)
            #print(resp)
            if(resp['state'] != 1):
                do_log(4, "初始化环境中断![admin]")
                return json({'state': -1, 'info':'初始化环境中断!','done': success,'total':total})
            success += 1
        do_log(2, "valid:初始化环境成功![admin]")
        return json({'state': 0, 'total': total})
    except Exception as e:
        #print(e)
        do_log(4, "Valid:OpenStack无响应")
        return json({'state': -2, 'info': 'Valid:OpenStack无响应'})


@bp_admin_user.post("/admin/user/role")
async def add_user(request):
    try:
        data = request.json
    except:
        do_log(4, "add_ur:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_insert("ur", created_at = time, updated_at = time, u_id = int(data['u_id']), r_id = int(data['r_id'])):
            do_log(2, "add_ur:ur添加成功！[user_id=%s]" % (data['u_id'],))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "add_ur:数据库操作失败[user_id=%s]" % (data['u_id'],))
            return json({'state': -2, 'info': '数据库操作失败'})
    except Exception as e:
        do_log(4, "add_ur:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_user.route("/admin/user", methods=['PATCH'])
async def update_user(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("user",set={ "updated_at":time, "name":data['name'], "email":data['email'], "resource_path":data['resource_path'], "stu_number":data['stu_number'], "phone":data['phone'],}, id=id):
            do_log(2, "update_user:用户信息修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_user:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_admin_user.route("/admin/user/mul/del", methods=['GET'])
async def delete_role(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_role:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

    try:
        total = 0
        success = 0
        uids = await db_select("ur", find=["u_id"], r_id=id)
        dictId = []
        for uid in uids:
            dictId.append(uid['u_id'])
            try:
                tids = await db_select("target", find=["template"], user=uid['u_id'], deleted=0)
                for tid in tids:
                    resp = await aio_delete(vmURL+'environment?'+'template_id='+str(tid['template'])+'&user_id='+str(uid['u_id']))
                    if resp['state'] == 1:
                        break
                    else:
                        do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
                        return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
            except Exception as e:
                do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
                return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
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


@bp_admin_user.route("/admin/user/passwd", methods=['PATCH'])
async def update_user(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("user",set={ "updated_at":time, "passwd":data['passwd']}, id=id):
            do_log(2, "update_user:用户信息修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_user:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_user.route("/admin/user/main", methods=['PATCH'])
async def update_user(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("user",set={ "updated_at":time, "name":data['name'], "email":data['email'], "stu_number":data['stu_number'], "phone":data['phone'],}, id=id):
            do_log(2, "update_user:用户信息修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_user:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_user.route("/admin/user/role", methods=['PATCH'])
async def update_user(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_userRole:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("ur",set={ "updated_at":time, "u_id" : int(data['u_id']), "r_id" : int(data['r_id'])}, id=id):
            do_log(2, "update_userRole:用户信息修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_userRole:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_userRole:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_user.route("/admin/user/del", methods=['GET'])
async def delete_user(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        tids = await db_select("target", find=["template"], user=id, deleted=0)
        for tid in tids:
            resp = await aio_delete(vmURL+'environment?'+'template_id='+str(tid['template'])+'&user_id='+str(id))
            if resp['state'] == 1:
                break
            else:
                do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
                return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
    except Exception as e:
        do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
        return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
    try:
        dictId = [id]
        data={"user_id_list": dictId}
        resp = await aio_put(vmURL+'user', data)
        if(resp['state'] != 1):
            do_log(4, "删除OpenStack后台账户失败!")
            return json({'state': -1, 'info':'删除OpenStack后台账户失败!'})
        do_log(2, "delete_user:用户删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    except:
        do_log(4, "delete_user:OpenStack交互失败！")
        return json({'state': -1, 'info': 'OpenStack交互失败！'})
        

@bp_admin_user.get("/admin/user")
async def get_user(request):
    """
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    return_info = await db_select("userView", user_id = id )
    """
    return_info = await db_select("userView")
    do_log(2, "get_user:用户信息查询成功![admin]")
    return json({'state': 0, 'user': return_info})

@bp_admin_user.post("/admin/searchUser")
async def search_user(request):
    try:
        data=request.json
        info=data['search']
    except:
        do_log(4, "search_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    sql="""select * from userView where user_name like "%%%s%%" or user_number like "%%%s%%" """ % (info,info)
    # #print(sql)
    try:
        conn = await aiomysql.connect(**db.config)
        cur = await conn.cursor(cursor=aiomysql.cursors.DictCursor)
        await cur.execute(sql)
        re=await cur.fetchall()
        await cur.close()
        conn.close()
        for r in re:
            r['created_at'] = str(r['created_at'])
    except Exception as e:
        #print(e)
        do_log(4, "search_user:数据库操作失败[search:%s]" % (info,))
        return json({"state":-2,'info':'数据库操作失败'})
    do_log(2, "search_user:用户查找成功！[search:%s]" % (info,))              
    return json({'state':0,'userCourse':re})



################################ROLE###################################################################################

@bp_admin_user.get("/admin/userGroup")
async def get_role(request):

    return_info = await db_select("role")
    do_log(2, "get_role:用户组查询成功![admin]")
    return json({'state': 0, 'userGroup': return_info})


@bp_admin_user.post("/admin/userGroup")
async def add_role(request):
    try:
        data = request.json
    except:
        do_log(4, "add_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_insert("role", updated_at = time, created_at = time, name = data['name'], description = data['description'], privilege = data['privilege']):
            do_log(2, "add_role:用户组添加成功！")
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "add_role:数据库操作失败")
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "add_role:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_admin_user.route("/admin/userGroup/check", methods=['GET'])
async def update_role(request):
    try:
        get_info = request.raw_args
        role_id = int(get_info['id'])
    except:
        do_log(4, "update_role:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        info = await db_select("ur", find=["u_id"], r_id=role_id)
        if info == None or info == []:
            do_log(2, "checkrole:用户组用户检查成功！[id=%d]" % (role_id,))
            return json({'state': 0, 'info': '用户组下无用户!'})
        else:
            do_log(4, "checkrole:用户组用户检查成功！[id=%d]" % (role_id,))
            return json({'state': -2, 'info': '用户组下有用户!','total': len(info)})
    except:
        do_log(4, "update_role:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_admin_user.route("/admin/userGroup", methods=['PATCH'])
async def update_role(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_role:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("role",set={ "updated_at":time, "name":data['name'], "description":data['description'], "privilege":data['privilege'],}, id=id):
            do_log(2, "update_role:用户组修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_role:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_role:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_admin_user.route("/admin/userGroup/del", methods=['GET'])
async def delete_role(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_role:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

    try:
        total = 0
        success = 0
        uids = await db_select("ur", find=["u_id"], r_id=id)
        dictId = []
        for uid in uids:
            dictId.append(uid['u_id'])
            try:
                tids = await db_select("target", find=["template"], user=uid['u_id'], deleted=0)
                for tid in tids:
                    resp = await aio_delete(vmURL+'environment?'+'template_id='+str(tid['template'])+'&user_id='+str(uid['u_id']))
                    if resp['state'] == 1:
                        break
                    else:
                        do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
                        return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
            except Exception as e:
                do_log(4, "delete_user:用户存在未关闭的实验，且删除环境失败。")
                return json({'state': -1, 'info': '用户存在未关闭的实验，且删除环境失败。'})
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

    if await db_delete("role", id=id):
        do_log(2, "delete_role:用户组删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "delete_role:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})