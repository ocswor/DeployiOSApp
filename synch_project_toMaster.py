# -*- coding: utf-8 -*-
# @Time    : 2017/11/12 下午4:42
# @Author  : Eric


import sys,subprocess
import os
from fabric.context_managers import cd, settings, lcd
from fabric.operations import run, local, put, sudo
import getopt


modified_path = '/Users/eric/Desktop/project/code/Taidi_newCarApp/' #修改过的项目路径
#destination_path = '/Users/eric/Desktop/project/code/Taidi_xiaoSanApp/'    #需要拷贝进去的项目路径
destination_path = '/Users/eric/Desktop/project/code/Taidi_ios/'    #需要拷贝进去的项目路径




def main():
    os.getcwd() #获取当前工作目录
    os.chdir(modified_path)
    print '修改项目路径%s \n'%(os.getcwd())
    modified_file = []
    added_file = []
    rev = subprocess.Popen('git status ', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    revList = rev.stdout.readlines()
    for line in revList:
        line = line.strip('\n').strip('\t')
        if (line.startswith('modified') and (line.endswith('.m') or line.endswith('.h'))):
            line_arr = line.split(' ')
            if len(line_arr)>0:
                line_res = line_arr[len(line_arr)-1]
                print '找到修改文件:%s' % line_res
                modified_file.append(line_res)
                line_path = modified_path+line_res
                copy_path = destination_path+line_res
                las_res = subprocess.Popen('cp %s %s'%(line_path,copy_path),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                error = las_res.stderr.readlines()
                if not las_res.stderr.readlines():
                    print '复制成功'
                else:
                    print '失败%s'%','.join(error)


        if line.startswith('new file'):
            line_arr = line.split(' ')
            if len(line_arr) > 0:
                line_res = line_arr[len(line_arr) - 1]
                print '找到新增文件:%s' % line_res
                added_file.append(line_res)
                line_path = modified_path + line_res
                copy_path = destination_path + line_res
                las_res = subprocess.Popen('cp %s %s' % (line_path, copy_path), shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE)
                error = las_res.stderr.readlines()
                if not las_res.stderr.readlines():
                    print '复制成功'
                    # os.chdir(destination_path)
                    # add_git = subprocess.Popen("git add %s" % line_res, shell=True, stdout=subprocess.PIPE,
                    #                        stderr=subprocess.PIPE)
                    # gitadd_error = las_res.stderr.readlines()
                    # if not gitadd_error:
                    #     print '添加 %s 成功'%line_res
                    # else:
                    #     print '添加 %s 失败'%','.join(gitadd_error)
                else:
                    print '失败%s' % ','.join(error)

    print '\n累计修改%s文件\n'%len(modified_file)
    for file in modified_file:
        print file

    print '\n新增%s文件\n 新增文件已经拷贝到项目目录需要在xcode工程中手动添加 右键 add files to \n '%len(added_file)
    for file in added_file:
        print file


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "u:o:d:")
    if len(opts) > 0:
        for op, value in opts:
            if op == '-f':
                modified_path = value
            if op == '-t':
                destination_path = value

    main()



