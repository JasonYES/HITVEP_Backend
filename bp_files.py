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

bp_files = Blueprint('bp_files')


#################
    #### ALL
fileGetpath = "/Files/"
pid_path = "pid"
    #### Weihai
# filepath = "/home/hjk/hitvepVue/Files/"
# port = 8000
# ospath = "/home/hjk/hitvepFile/os/"
# vmURL = "http://172.29.152.243:3560/"
    #### Harbin
filepath = "/home/hit/HITVEP/Frontend/Files/"
port = 3561
ospath = "/home/hit/HITVEP/UploadFiles/"
vmURL = "http://192.168.69.28:3560/"
#################



@bp_files.route("/files", methods=['POST'])
async def files(request):
    try:
        # #print(dir(request))
        # #print(dir(request.stream._format))
        file = request.files.get('file')
        if not file:
            do_log(4, "文件为空")
            return json({'state': -1, 'info': '操作失败'})
        filefix = file.name.split('.')[-1]
        filenameS = str(uuid.uuid4()) + '.' +filefix
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        async with aiofiles.open( filepath + filenameS , 'wb+') as f:
            await f.write(file.body)
            # #print(str(file.name + filenameS ))
            return json({ "state": 0, "state":file.name ,"time": time,"res": fileGetpath +filenameS })
    except Exception as e:
        #print(e)
        do_log(4, "file_upload:upload failed")
        return json({'state': -1, 'info': 'file_upload:upload failed'})


@bp_files.route("/down/reports", methods=['POST'])
async def files(request):
    try:
        info = request.json
        c_id = int(info['c_id'])
        ci_id = info['ci_id']
        ci_name = info['ci_name']
    except:
        do_log(4, "get_report:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        time = datetime.datetime.now().strftime("%Y%m%d")
        zipName = ci_name + '_' + time + '.zip'
        z = zipfile.ZipFile(filepath+zipName,'w',compression=zipfile.ZIP_STORED)
        # z.write(filepath+'b660e7d0-dc58-40f0-9de4-5cc3fa788ff8.pdf','newname')
    except:
        do_log(4, "get_report:压缩文件创建失败！")
        return json({'state': -1, 'info': '压缩文件创建失败！'})
    try:
        studata=await db_select("userCourseRole",c_id=c_id)
        for stu in studata:
            if stu['report_res'] != None and stu['report_res'] != '':
                report_res = innerjson.loads(stu['report_res'])
                for report in report_res:
                    if(report.get(str(ci_id))!=None):
                        file = report.get(str(ci_id)).get('path')
                        file = file.split('/')[-1]
                        tail = '.' + file.split('.')[-1]
                        newname = '/'+ stu['r_name'] +'/' +stu['stu_number']+'-'+stu['u_name'] +tail
                        if os.path.exists(filepath+file):
                            z.write(filepath+file, newname)
        z.close()
        return json({'state': 0, 'info': fileGetpath+zipName})
    except:
        do_log(4, "get_report:压缩文件写入失败！")
        return json({'state': -1, 'info': '压缩文件写入失败！'})


@bp_files.route("/check/reports", methods=['POST'])
async def files(request):
    try:
        info = request.json
        c_id = int(info['c_id'])
        ci_id = info['ci_id']
        ci_name = info['ci_name']
    except:
        do_log(4, "get_report:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:

        studata=await db_select("userCourseRole",c_id=c_id)
        for stu in studata:
            if stu['report_res'] != None and stu['report_res'] != '':
                report_res = innerjson.loads(stu['report_res'])
                for report in report_res:

                    if(report.get(str(ci_id))!=None):
                        reportTime = report.get(str(ci_id)).get('size')
                        stu['report_res']=reportTime
                        break
                    else:
                        stu['report_res']=None

        return json({'state': 0, 'student': studata})
    except:
        do_log(4, "get_report:数据库错误。")
        return json({'state': -1, 'info': '数据库错误。'})


@bp_files.route("/excel/store", methods=['POST'])
async def files(request):
    try:
        file = request.files.get('file')
        if not file:
            do_log(4, "文件为空")
            return json({'state': -1, 'info': '操作失败'})
        filefix = file.name.split('.')[-1]
        filenameS = str(uuid.uuid4()) + '.' +filefix
        async with aiofiles.open( filepath + filenameS , 'wb+') as f:
            await f.write(file.body)
            # #print(str(file.name + filenameS ))
            return json({ "state": 0, "state":file.name , "res": filepath +filenameS })
    except Exception as e:
        #print(e)
        do_log(4, "file_upload:upload failed")
        return json({'state': -1, 'info': 'file_upload:upload failed'})

@bp_files.route("/osfiles", methods=['POST'])
async def files(request):
    try:
        file = request.files.get('file')
        if not file:
            do_log(4, "文件为空")
            return json({'state': -1, 'info': '操作失败'})
        filefix = file.name.split('.')[-1]
        filenameS = ospath + str(uuid.uuid4()) + '.' +filefix
        async with aiofiles.open( filenameS , 'wb+') as f:
            await f.write(file.body)
            # #print(str(file.name + filenameS ))
            return json({ "state": 0, "state":file.name , "res": filenameS })
    except Exception as e:
        #print(e)
        do_log(4, "file_upload:upload failed")
        return json({'state': -1, 'info': 'file_upload:upload failed'})


@bp_files.route("/files/excel", methods=['POST'])
async def files(request):
    try:
        jsondata=request.json
    except:
        do_log(4, "update_uc:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    try:
        data = xlrd.open_workbook(jsondata['file'])
    except Exception as e:
        #print(e)
        do_log(4, "excel open:failed")
        return json({'state': -1, 'info': 'failed to open excel'})
    try:
        table = data.sheets()[0]
        total = 0
        failed = 0
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for rownum in range(table.nrows):
            row = table.row_values(rownum)
            number = str(row[0]).split('.')[0]
            name = str(row[1])
            phone = str(row[2]).split('.')[0]
            md5 = hashlib.md5()
            md5.update(number.encode('utf-8'))
            password = md5.hexdigest()
            if(number=="" or name==""):
                failed += 1 
                continue
            if await db_insert("user", created_at=time, updated_at=time, stu_number=number, name=name, passwd = password, phone=phone ):
                u_id= await db_select("user",find=["id"], updated_at=time,created_at=time, stu_number=number, name=name)  
                if await db_insert("ur", created_at=time, updated_at=time, u_id=int(u_id[0]['id']), r_id=int(jsondata['role'])):
                    total += 1            
        do_log(2, "Ecxel-users succeed.")
        return json({'state': 0, 'info': 'Ecxel-users succeed.', 'total':total})
    except Exception as e:
        #print(e)
        do_log(4, "file_upload: database insert failed")
        return json({'state': -1, 'info': 'database insert failed'})

@bp_files.route("/report/student", methods=['PATCH'])
async def update_ucx(request):
    get_info = request.raw_args
    try:
        id = int(get_info['id'])
        data=request.json
        report=data['report']
    except:
        do_log(4, "update_uc:参数缺失或不规范")
        return json({'state': -1, 'info': '参数缺失或不规范'})
    if await db_update("uc",set={"report_res":report},id=id):
        do_log(2,"update_uc:报告修改成功！[id=%d]" % (id,))
        return json({'state':0,'info':'成功'})
    else:
        do_log(2,"update_uc:数据库操作失败[id=%d]" % (id,))
        return json({'state':-1,'info':'数据库操作失败'})
