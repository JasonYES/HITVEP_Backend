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

bp_tea_main = Blueprint('bp_tea_main')

###################################SOFTWARE#################################################################################



@bp_tea_main.route("/teacher/software/del", methods=['GET'])
async def delete_software(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_delete("software", id=id):
        do_log(2, "delete_software:软件删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "delete_software:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})


@bp_tea_main.post("/teacher/software")
async def add_software(request):
    try:
        data = request.json
        assert len(data) == 4
    except:
        do_log(4, "add_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_insert("software",updated_at=time,created_at=time,name=data['name'],description=data['description'],author=int(data['author']),is_public=int(data['is_public'])):
            do_log(2, "add_software:软件添加成功！[name=%s]" % (data['name'],))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "add_software:数据库操作失败[name=%s]" % (data['name'],))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "add_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})




@bp_tea_main.route("/teacher/software", methods=['PATCH'])
async def update_software(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
        data = request.json
        assert len(data) == 4
    except:
        do_log(4, "update_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("software",set={"updated_at":time,"name":data['name'],"description":data['description'],"author":int(data['author']),"is_public":int(data['is_public'])},id=id):
            do_log(2, "update_software:软件修改成功！[id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_software:数据库操作失败[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})





@bp_tea_main.get("/teacher/software")
async def get_software(request):
    try:
        get_info = request.raw_args
        id = int(get_info['id'])
    except:
        do_log(4, "get_software:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    softwares=await db_select("software",find=["id","name","resource_path","description","is_public"],author=id)
    do_log(2, "get_software:软件信息查询成功！[id=%d]" % (id,))
    return json({"state":0,"software":softwares})



################################TEMPLATE####################################################################################


@bp_tea_main.post("/teacher/course/template")
async def add_template(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        user_id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "add_template:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        images={}
        softwares={}
        flavors={}
        for i in range(0,len(data)):
            host="host"+str(i+1)
            images[host]=data[i]['image']
            softtran = []
            for soft in data[i]['soft']:
                softtran.append(str(soft))
            softwares[host]=softtran
            flavors[host]=data[i]['flavor']
        imagesX={}
        softwaresX={}
        flavorsX={}
        switch=["RegionOne","RegionTwo","RegionThree","Region"]
        for swit in switch:
            imagesX[swit]=images
            softwaresX[swit]=softwares
            flavorsX[swit]=flavors
    except Exception as e:
        do_log(4, "add_template:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        if await db_insert("template",updated_at=time,created_at=time,image_list=innerjson.dumps(imagesX),sw_list=innerjson.dumps(softwaresX),flavor_list=innerjson.dumps(flavorsX),state='0'):
            tids = await db_select("template",find=["id"],updated_at=time,created_at=time,image_list=innerjson.dumps(imagesX),sw_list=innerjson.dumps(softwaresX),flavor_list=innerjson.dumps(flavorsX))     
    except Exception as e:
        do_log(4,"add_template:数据库操作失败[id=%d]" % (id,))
        return json({'state':-2,'info':'数据库操作失败'})
    try:
        if await db_update("courseItem",set={"template":int(tids[0]['id'])},id=id):
            do_log(2,"add_template:新增模板成功！[id=%d]" % (id,))
            return json({'state':0,'info':'成功'})
        else:
            do_log(4,"add_template:数据库操作失败[id=%d]" % (id,))
            return json({'state':-2,'info':'数据库操作失败'})
    except Exception as e:
        await db_delete("template", id=int(tids[0]['id']))
        do_log(4,"add_template:数据库操作失败[id=%d]" % (id,))
        return json({'state':-2,'info':'数据库操作失败'})


@bp_tea_main.route("/teacher/course/template", methods=['GET'])
async def update_template(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "select_template:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    template = await db_select("template", id=id)
    # #print(course)
    # if len(course) < 1:
    #    do_log(2, "select_course:该教师无课程[id=%d]" % (id,))
    #    return json({'state': 1, 'info': '该教师无课程'})
    do_log(2, "select_template:template查询成功![id=%d]" % (id,))
    return json({'state': 0, 'template': template})



@bp_tea_main.route("/teacher/course/template", methods=['PATCH'])
async def update_template(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_template:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        images={}
        softwares={}
        flavors={}
        for i in range(0,len(data)):
            host="host"+str(i+1)
            images[host]=data[i]['image']
            softwares[host]=data[i]['soft']
            flavors[host]=data[i]['flavor']
    except:
        do_log(4, "update_template:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})#################################################
    if await db_update("template",set={"updated_at":time,"image_list":str(images),"sw_list":str(softwares),"flavor_list":str(flavors)},id=id):
        do_log(2, "update_template:[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "update_template:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})


##########################USERCOURSE####################################################################################


@bp_tea_main.get("/teacher/student")
async def get_userCourse(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_userCourse:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    info=await db_select("userCourse",course_author=id)
    ##print(info)
    #infos=[]
    #for i in info:
    #   infos.append({'uc_id':i[0],'user_id':i[1],'course_id':i[2],'role_id':i[3],'course_author':i[4],'user_name':i[5],'user_email':i[6],'user_number':i[7],'user_phone':i[8],'course_name':i[9],'course_res':i[10],'course_state':i[11],'role_name':i[12],'role_description':i[13],'uc_state':i[14],'course_expired':i[15]})
    return json({'state':0,'userCourse':info})

@bp_tea_main.post("/teacher/searchSC")
async def search_userCourse(request):
    try:
        data=request.json
        info=data['search']
        tid=int(data['id'])
    except:
        do_log(4, "search_userCourse:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    sql="""select * from userCourse where (user_name like "%%%s%%" or user_number like "%%%s%%" or course_name like "%%%s%%") and course_author=%d""" % (info,info,info,tid)
    try:
        conn = await aiomysql.connect(**db.config)
        cur = await conn.cursor(cursor=aiomysql.cursors.DictCursor)
        await cur.execute(sql)
        re=await cur.fetchall()
        await cur.close()
        conn.close()
    except Exception as e:
        ##print(e)
        return json({"state":-2,'info':'数据库操作失败'})
               
    return json({'state':0,'userCourse':re})

@bp_tea_main.get("/admin/publish/userGroup")
async def get_role(request):

    return_info = await db_select("role", privilege='STUDENT')
    do_log(2, "get_role:用户组查询成功![admin]")
    return json({'state': 0, 'userGroup': return_info})


@bp_tea_main.route("/teacher/publish", methods=['POST'])
async def new_uc(request):
    get_info = request.raw_args
    try:
        c_id = int(get_info['id'])
        data=request.json
        role=data['role']
    except:
        do_log(4, "update_uc:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    for rol in role:
        info=await db_select("ur", find=["u_id"], r_id=int(rol))
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for inf in info:
            #print(inf['u_id'])
            try_get=await db_select("uc",c_id=c_id,u_id=inf['u_id'])
            if not (try_get == []):
                continue
            try:
                if await db_insert("uc",updated_at=time,created_at=time,u_id=inf['u_id'],c_id=c_id,state=''):
                    do_log(2,"add:新增选课成功！[id=%d]" % (inf['u_id']))
            except Exception as e:
                #print(e)
                do_log(4,"add:新增选课失败！[id=%d]" % (inf['u_id']))    
                return json({'state':-1,'info':'数据库插入失败'})
    do_log(2,"insert_uc:用户组发布成功!")
    return json({'state':0,'info':'成功'})


@bp_tea_main.route("/teacher/student", methods=['PATCH'])
async def update_uc(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data=request.json
        score=int(data['score'])
    except:
        do_log(4, "update_uc:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_update("uc",set={"score":score},id=id):
        do_log(2,"update_uc:成绩修改成功！[id=%d]" % (id,))
        return json({'state':0,'info':'成功'})
    else:
        do_log(2,"update_uc:数据库操作失败[id=%d]" % (id,))
        return json({'state':-1,'info':'数据库操作失败'})


@bp_tea_main.route("/teacher/student/del", methods=['GET'])
async def delete_uc(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_uc:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_delete("uc",id=id):
        do_log(2,"delete_uc:学生课程删除成功！[id=%d]" % (id,))
        return json({'state':0,'info':'学生课程删除成功！'})
    else:
        do_log(2,"delete_uc:数据库操作失败[id=%d]" % (id,))
        return json({'state':-2,'info':'数据库操作失败'})