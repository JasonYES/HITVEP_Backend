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

bp_course = Blueprint('bp_course')

# 获取某个学生的课程

@bp_course.get("/course/state")
async def course_state(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "select_course:id不规范或不存在")
        return json({'state': -1, 'info': 'id不规范或不存在'})
    course = await db_select("userCourse", user_id=id)
    time = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    do_log(2, "select_course:课程查询成功![id=%d]" % (id,))
    return json({'state': 0, 'course': course, 'time': time})

# 获取某个教师的课程


@bp_course.get("/course/teacher")
async def course_get(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "select_course:id不规范或不存在")
        return json({'state': -1, 'info': 'id不规范或不存在'})
    course = await db_select("teacherView", author=id)
    
    do_log(2, "select_course:课程查询成功![id=%d]" % (id,))
    return json({'state': 0, 'course': course})


@bp_course.get("/course/admin")
async def course_get(request):
    course = await db_select("teacherView")
    
    do_log(2, "select_course:课程查询成功![id=%d]")
    return json({'state': 0, 'course': course})

# 选课操作


@bp_course.route("/course/choose", methods=['PATCH'])
async def update_course(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
        # assert len(data) == 1
    except:
        do_log(4, "update_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("uc", set={'updated_at': time, 'state': data['state']}, id=id):
            do_log(2, "update_course:课程更新成功![id=%d]" % (id,))
            return json({'state': 0, 'info': '操作成功'})
        else:
            do_log(4, "update_course:写入数据库时发生错误[id=%d]" % (id,))
            return json({'state': -2, 'info': '写入数据库时发生错误'})
    except:
        do_log(4, "update_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


#获取课程item

@bp_course.get("/course/item")
async def get_userCourseItem(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    info=await db_select("courseItem",id=id)
    return json({'state':0,'courseItem':info})


#获取一个课程的信息
@bp_course.get("/course/one")
async def get_userCourseOne(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    info=await db_select("teacherView",id=id)
    return json({'state':0,'courseItem':info})

#获取一个UC
@bp_course.get("/course/uc")
async def get_userCourseOne(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    info=await db_select("userCourse",uc_id=id)
    return json({'state':0,'userCourse':info})