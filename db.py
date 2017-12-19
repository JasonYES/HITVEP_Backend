import sqlalchemy as sa
from aiomysql.sa import create_engine
import logging
#数据库配置
config = {
          'user':'root', 
          'db':'hit_vep_v4',
          'host':'172.29.152.246', 
          'password':'hitnslab',  
          # 'host':'192.168.69.28', 
          # 'password':'hitrjzx', 
          'charset':'utf8'
          }

#Alchemy框架的使用
metadata = sa.MetaData()

user = sa.Table('user', metadata,
    sa.Column('created_at', sa.DateTime),
    sa.Column('updated_at', sa.DateTime),
    sa.Column('deleted_at', sa.DateTime),
    sa.Column('deleted', sa.Integer),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('passwd', sa.String(255)),
    sa.Column('salt', sa.String(255)),
    sa.Column('email', sa.String(255)),
    sa.Column('op_user', sa.String(50)),
    sa.Column('op_project', sa.String(50)),
    sa.Column('resource_path', sa.String(255)),
    sa.Column('stu_number', sa.String(255)),
    sa.Column('phone', sa.String(255)),
    sa.Column('op_passwd', sa.String(50)),
    sa.Column('op_username', sa.String(50)),
    sa.Column('region_id', sa.String(50))
    )

course = sa.Table('course',metadata,
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('description',sa.Text),
        sa.Column('author', sa.Integer),
        sa.Column('resource_path',sa.String(255)),
        sa.Column('expired_at', sa.DateTime),
        sa.Column('state',sa.Text),
        sa.Column('intro',sa.Text)
        )

courseChapter = sa.Table('courseChapter',metadata,
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('parent', sa.Integer)
        )

courseItem = sa.Table('courseItem',metadata,
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255)),
        sa.Column('parent', sa.Integer),
        sa.Column('about_item', sa.Text),
        sa.Column('about_exp', sa.Text),
        sa.Column('parameter', sa.Text),
        sa.Column('extra', sa.Text),
        sa.Column('resource_path', sa.String(255)),
        sa.Column('resource_name', sa.String(255)),
        sa.Column('template', sa.Integer)
        )

uc = sa.Table('uc',metadata,
    sa.Column('created_at', sa.DateTime),
    sa.Column('updated_at', sa.DateTime),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('u_id', sa.Integer),
    sa.Column('c_id', sa.Integer),
    sa.Column('state', sa.Text),
    sa.Column('report_res', sa.Text),
    sa.Column('score', sa.Integer),
    )

userCourseRole = sa.Table('userCourseRole',metadata,
    sa.Column('uc_id', sa.Integer),
    sa.Column('u_id', sa.Integer),
    sa.Column('c_id', sa.Integer),
    sa.Column('r_id', sa.Integer),

    sa.Column('u_name', sa.String(255)),
    sa.Column('stu_number', sa.String(255)),

    sa.Column('r_name', sa.String(255)),
    sa.Column('description', sa.String(255)),
    sa.Column('report_res', sa.Text),
    )


ur = sa.Table('ur',metadata,
    sa.Column('created_at', sa.DateTime),
    sa.Column('updated_at', sa.DateTime),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('u_id', sa.Integer),
    sa.Column('r_id', sa.Integer),
    )

role = sa.Table('role',metadata,
    sa.Column('created_at', sa.DateTime),
    sa.Column('updated_at', sa.DateTime),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('name', sa.String(255)),
    sa.Column('description', sa.String(255)),
    sa.Column('privilege', sa.String(255)),
    )

flavor = sa.Table('flavor', metadata,
                  sa.Column('created_at', sa.DateTime),
                  sa.Column('updated_at', sa.DateTime),
                  sa.Column('deleted_at', sa.DateTime),
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('deleted', sa.Integer),
                  sa.Column('name', sa.String(255)),
                  sa.Column('author', sa.Integer),
                  sa.Column('ram', sa.Integer),
                  sa.Column('cpu', sa.Integer),
                  )

flavorView = sa.Table('flavorView', metadata,
                  sa.Column('created_at', sa.DateTime),
                  sa.Column('updated_at', sa.DateTime),
                  sa.Column('id', sa.Integer, primary_key=True),
                  sa.Column('name', sa.String(255)),
                  sa.Column('author', sa.Integer),
                  sa.Column('ram', sa.Integer),
                  sa.Column('cpu', sa.Integer),
                  sa.Column('user_name', sa.String(255)),
                  sa.Column('user_email', sa.String(255)),
                  sa.Column('user_phone', sa.String(255)),
                  )

userTemplate = sa.Table('userTemplate',metadata,
    sa.Column('u_id', sa.Integer),
    sa.Column('c_id', sa.Integer),
    sa.Column('cc_id', sa.Integer),
    sa.Column('ci_id', sa.Integer),

    sa.Column('c_name', sa.String(255)),
    sa.Column('cc_name', sa.String(255)),
    sa.Column('ci_name', sa.String(255)),

    sa.Column('template', sa.Integer),
    sa.Column('parameter', sa.Text),
    )

software = sa.Table('software', metadata,
                    sa.Column('created_at', sa.DateTime),
                    sa.Column('updated_at', sa.DateTime),
                    sa.Column('deleted_at', sa.DateTime),
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String(255)),
                    sa.Column('deleted', sa.Integer),
                    sa.Column('resource_path', sa.String(255)),
                    sa.Column('description', sa.String(255)),
                    sa.Column('author', sa.Integer),
                    sa.Column('is_public', sa.Integer)
                    )

softwareView = sa.Table('softwareView', metadata,
                    sa.Column('created_at', sa.DateTime),
                    sa.Column('updated_at', sa.DateTime),
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String(255)),
                    sa.Column('resource_path', sa.String(255)),
                    sa.Column('description', sa.String(255)),
                    sa.Column('author', sa.Integer),
                    sa.Column('is_public', sa.Integer),
                    sa.Column('user_name', sa.String(255)),
                    sa.Column('user_email', sa.String(255)),
                    sa.Column('op_user', sa.String(50)),
                    sa.Column('user_phone', sa.String(255)),
                    )

image = sa.Table('image', metadata,
                    sa.Column('created_at', sa.DateTime),
                    sa.Column('updated_at', sa.DateTime),
                    sa.Column('deleted_at', sa.DateTime),
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String(255)),
                    sa.Column('deleted', sa.Integer),
                    sa.Column('author', sa.Integer),
                    sa.Column('resource_path', sa.String(255)),
                    sa.Column('container_format', sa.String(50)),
                    sa.Column('disk_format', sa.String(50)),
                    )

imageView = sa.Table('imageView', metadata,
                    sa.Column('created_at', sa.DateTime),
                    sa.Column('updated_at', sa.DateTime),
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('name', sa.String(255)),
                    sa.Column('author', sa.Integer),
                    sa.Column('resource_path', sa.String(255)),
                    sa.Column('container_format', sa.String(50)),
                    sa.Column('disk_format', sa.String(50)),
                    sa.Column('user_name', sa.String(255)),
                    sa.Column('user_email', sa.String(255)),
                    sa.Column('user_phone', sa.String(255)),
                    )

template = sa.Table('template', metadata,
                    sa.Column('created_at', sa.DateTime),
                    sa.Column('updated_at', sa.DateTime),
                    sa.Column('deleted_at', sa.DateTime),
                    sa.Column('id', sa.Integer, primary_key=True),
                    sa.Column('deleted', sa.Integer),
                    sa.Column('image_list', sa.String(255)),
                    sa.Column('sw_list', sa.String(255)),
                    sa.Column('flavor_list', sa.String(255)),
                    sa.Column('state', sa.String(255))
                    )

userCourse = sa.Table('userCourse',metadata,
    
    sa.Column('uc_id', sa.Integer),
    sa.Column('uc_state', sa.Text),
    sa.Column('score', sa.Integer),
    sa.Column('report_res', sa.Text),

    sa.Column('course_id', sa.Integer),
    sa.Column('course_name', sa.String(255)),
    sa.Column('course_res',sa.String(255)),
    sa.Column('course_expired', sa.DateTime),
    sa.Column('course_author', sa.Integer),
    sa.Column('course_state',sa.Text),

    sa.Column('user_id', sa.Integer),
    sa.Column('user_name', sa.String(255)),
    sa.Column('user_email', sa.String(255)),
    sa.Column('user_number', sa.String(255)),
    sa.Column('user_phone', sa.String(255)),

    sa.Column('role_id', sa.Integer),
    sa.Column('role_name', sa.String(255)),
    sa.Column('role_description',sa.String(255)),

    sa.Column('t_name',sa.String(255)),
    sa.Column('description',sa.Text),
    sa.Column('intro',sa.Text)
    )

userView = sa.Table('userView',metadata,

    sa.Column('user_id', sa.Integer),
    sa.Column('user_name', sa.String(255)),
    sa.Column('user_passwd', sa.String(255)),
    sa.Column('user_email', sa.String(255)),
    sa.Column('user_number', sa.String(255)),
    sa.Column('user_phone', sa.String(255)),
    sa.Column('user_res', sa.String(255)),
    sa.Column('created_at', sa.DateTime),

    sa.Column('role_id', sa.Integer),
    sa.Column('ur_id', sa.Integer),
    sa.Column('op_user', sa.String(50)),
    sa.Column('role_name', sa.String(255)),
    sa.Column('role_description',sa.String(255)),
    sa.Column('role_privilege',sa.String(255)),
    )

teacherView = sa.Table('teacherView',metadata,

    sa.Column('id', sa.Integer),
    sa.Column('name', sa.String(255)),
    sa.Column('resource_path',sa.String(255)),
    sa.Column('expired_at', sa.DateTime),
    sa.Column('author', sa.Integer),
    sa.Column('state',sa.Text),

    sa.Column('t_name',sa.String(255)),
    sa.Column('description',sa.Text),
    sa.Column('intro',sa.Text),
    )

courseTemplate = sa.Table('courseTemplate',metadata,

    sa.Column('created_at', sa.DateTime),
    sa.Column('c_name', sa.String(255)),
    sa.Column('cc_name', sa.String(255)),
    sa.Column('ci_name', sa.String(255)),
    sa.Column('template', sa.Integer),
    sa.Column('state', sa.String(255))
    )

target = sa.Table('target',metadata,

    sa.Column('created_at', sa.DateTime),
    sa.Column('updated_at', sa.DateTime),
    sa.Column('deleted_at', sa.DateTime),
    sa.Column('id', sa.Integer, primary_key=True),
    sa.Column('deleted', sa.Integer),
    sa.Column('name', sa.String(255)),


    )