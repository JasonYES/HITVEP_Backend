# -*- coding: utf-8 -*-
import asyncio
import datetime
import logging
import aiomysql
from sanic import Sanic
from sanic import response
from sanic.response import json
from aiomysql.sa import create_engine
from db_support import db_select, db_insert, db_delete, db_update, alchemyencoder
from db_support import aio_post, aio_delete, aio_put, aio_patch
import db
from sanic.log import log
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
from log_support import LOGGING
from log_support import do_log

from bp_course import bp_course
from bp_openstack import bp_openstack
from bp_files import bp_files
from bp_tea_course import bp_tea_course
from bp_tea_main import bp_tea_main
from bp_admin_user import bp_admin_user
from bp_admin_main import bp_admin_main

from config import *

app = Sanic(__name__)
app.config.REQUEST_MAX_SIZE = 4000000000
app.config.REQUEST_TIMEOUT = 1800

app.blueprint(bp_course)
app.blueprint(bp_openstack)
app.blueprint(bp_files)
app.blueprint(bp_tea_course)
app.blueprint(bp_tea_main)
app.blueprint(bp_admin_user)
app.blueprint(bp_admin_main)


#用户登录
@app.route("/login", methods=['POST'])
async def test(request):
    userform = request.json
    
    if(userform == None):
        return json({ "state": 0 , "info": "登录表单为空！"})  #登录失败：表单无内容

    try:
        if('username' in userform and userform['username'] != None):
            user = await db_select("userView", user_number=userform['username'])
            #print(user)
            if(user == []):
                return json({ "state": -1, "info": "用户名不存在！" })    
            if(user[0]['user_passwd'] == userform['password']):
                return json({ "state": 0, "info": user })  #登录成功
            else:
                return json({ "state": -1, "info": "密码错误"})  #登录失败：密码错误
    except Exception as e:
        #print(e)
        do_log(4, "用户登录失败![id=%d]" )
        return json({ "state": 0, "info": "登录失败！"})  #登录失败：其他


#########  个人信息   ###########################################


@app.get("/info/user")
async def get_userCourseOne(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
    except:
        do_log(4, "get_user:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    info=await db_select("user",id=id)
    return json({'state':0,'user':info})

async def save_pid():
    with open(pid_path, "a") as f:
        f.write(str(os.getpid())+"\n")


def start():
    try:
        with open(pid_path, "a") as f:
            f.write(str(os.getpid())+"\n")

        app.add_task(save_pid())
        app.run(host = "0.0.0.0", port = port,log_config=LOGGING, workers=4)
    except Exception as e:
        do_log(4, "start failed!")
        raise

def stop():
    try:
        with open(pid_path, "r") as f:
            processes = f.readlines()
            for p in processes:
                try:
                    a = os.kill(int(p[:-1]), signal.SIGKILL)
                except Exception as e:
                    do_log(4, str(e))
        open(pid_path, "w+")
        do_log(2, "sanic stop OK!")
    except Exception as e:
        do_log(4, "Error ocurred when trying to kill the processes Info: %s" % str(e)) 
        raise



