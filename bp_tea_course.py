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

bp_tea_course = Blueprint('bp_tea_course')

@bp_tea_course.route("/teacher/course/del", methods=['GET'])  # 删除课程
async def delete_course(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "Delete_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    # 由于外键，只对一个course表进行删除，chapter和item表的相关信息会自己清除
    if await db_delete("course", id=id):
        do_log(2, "delete_course:课程删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
       # logging.critical
        do_log(4, "delete_course:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})


# 获取某个教师的课程
@bp_tea_course.get("/teacher/course")
async def get_course(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "select_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    course = await db_select("course", author=id)
    # #print(course)
    # if len(course) < 1:
    #    do_log(2, "select_course:该教师无课程[id=%d]" % (id,))
    #    return json({'state': 1, 'info': '该教师无课程'})
    do_log(2, "select_course:课程查询成功![id=%d]" % (id,))
    return json({'state': 0, 'course': course})


# 课程内容更改
@bp_tea_course.route("/teacher/course", methods=['PATCH'])
async def update_course(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
        # assert len(data) == 5
    except:
        do_log(4, "update_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("course", set={'updated_at': time, 'name': data['name'], 'description': data['description'], 'intro': data['intro'], 'resource_path': data['resource_path'], 'expired_at': data['expired_at']}, id=id):
            do_log(2, "update_course:课程更新成功![id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_course:写入数据库时发生错误[id=%d]" % (id,))
            return json({'state': -2, 'info': '写入数据库时发生错误'})
    except:
        do_log(4, "update_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


# 课程内容更改
@bp_tea_course.route("/teacher/course/material", methods=['PATCH'])
async def update_course(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("course", set={'updated_at': time, 'state': data['state']}, id=id):
            do_log(2, "update_course:课程更新成功![id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_course:写入数据库时发生错误[id=%d]" % (id,))
            return json({'state': -2, 'info': '写入数据库时发生错误'})
    except:
        do_log(4, "update_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


# 添加新课程(course)
@bp_tea_course.post("/teacher/course")
async def add_course(request):
    try:
        data = request.json
        assert len(data) == 7
    except:
        do_log(4, "insert_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_insert("course", created_at=time, updated_at=time, name=data['name'], description=data['description'], author=int(data['author']), resource_path=data['resource_path'], expired_at=data['expired_at'], state=data['state'], intro=data['intro']):
            do_log(2, "insert_course:添加课程成功![name=%s]" % (data['name'],))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "insert_course:写入数据库时发生错误[name=%s]" % (data['name'],))
            return json({'state': -2, 'info': '写入数据库时发生错误'})
    except:
        do_log(4, "insert_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_tea_course.post("/teacher/course/structure/chapter")
async def add_chapter(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
        dname=data['name']
    except:
        do_log(4, "insert_chapter:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if await db_insert("courseChapter", name=dname, parent=id, updated_at=time, created_at=time):
        do_log(2, "insert_chapter:添加章节成功![parent=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "insert_chapter:写入数据库时发生错误[parent=%d]" % (id,))
        return json({'state': -2, 'info': '写入数据库时发生错误'})


@bp_tea_course.post("/teacher/course/structure/item")
async def add_item(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
        dname=data['name']
    except:
        do_log(4, "insert_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if await db_insert("courseItem", name=dname, parent=id, updated_at=time, created_at=time):
        do_log(2, "insert_item:添加课节成功![parent=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "insert_item:写入数据库时发生错误[parent=%d]" % (id,))
        return json({'state': -2, 'info': '写入数据库时发生错误'})


@bp_tea_course.get("/teacher/course/structure")
async def show_course(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "show_course:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    course_detail = []
    chapters = await db_select("courseChapter", find=["id", "name"], parent=id)
    for i in chapters:
        item = await db_select("courseItem", find=["id", "name"], parent=i['id'])
        course_detail.append({"chapter": i, "item": item})
    do_log(2,"show_course:查询课程详细信息成功！[id=%d]" % (id,))
    return json({'state': 0, 'course': course_detail})


@bp_tea_course.route("/teacher/course/structure/chapter", methods=['PATCH'])
async def update_chapter(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
        dname=data['name']
    except:
        do_log(4, "update_chapter:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if await db_update("courseChapter", set={"updated_at": time, "name": dname}, id=id):
        do_log(2, "update_chapter:章节更新成功![id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "update_chapter:写入数据库时发生错误[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})


@bp_tea_course.route("/teacher/course/item/extra", methods=['PATCH'])
async def update_item(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("courseItem", set={"updated_at": time, "extra": data['extra']}, id=id):
            do_log(2, "update_item:课节更新成功![id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_item:写入数据库时发生错误[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_tea_course.route("/teacher/course/structure/item", methods=['PATCH'])
async def update_item(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("courseItem", set={"updated_at": time, "name": data['name']}, id=id):
            do_log(2, "update_item:课节更新成功![id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_item:写入数据库时发生错误[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_tea_course.route("/teacher/course/resource/item", methods=['PATCH'])
async def update_item(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("courseItem", set={"updated_at": time, "resource_name": data['resource_name'],"resource_path": data['resource_path']}, id=id):
            do_log(2, "update_item:课节更新成功![id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_item:写入数据库时发生错误[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})

@bp_tea_course.route("/teacher/course/exp/item", methods=['PATCH'])
async def update_item(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data = request.json
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        if await db_update("courseItem", set={"updated_at": time, "parameter": data['parameter'],"about_item": data['about_item'],"about_exp": data['about_exp']}, id=id):
            do_log(2, "update_item:课节更新成功![id=%d]" % (id,))
            return json({'state': 0, 'info': '成功'})
        else:
            do_log(4, "update_item:写入数据库时发生错误[id=%d]" % (id,))
            return json({'state': -2, 'info': '数据库操作失败'})
    except:
        do_log(4, "update_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})


@bp_tea_course.route("/teacher/course/structure/chapter/del", methods=['GET'])
async def delete_chapter(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_chapter:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_delete("courseChapter", id=id):
        do_log(2, "delete_chapter:章节删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "delete_chapter:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})


@bp_tea_course.route("/teacher/course/structure/item/del", methods=['GET'])
async def delete_item(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "delete_item:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_delete("courseItem", id=id):
        do_log(2, "delete_item:课节删除成功[id=%d]" % (id,))
        return json({'state': 0, 'info': '成功'})
    else:
        do_log(4, "delete_item:数据库操作失败[id=%d]" % (id,))
        return json({'state': -2, 'info': '数据库操作失败'})