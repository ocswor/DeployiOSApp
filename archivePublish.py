# -*- coding: utf-8 -*-
# @Time    : 2017/12/1 下午2:02
# @Author  : Eric
import datetime
import os
import subprocess
import requests
import sendEmail
import sys
import getopt
from config import *

CONFIGURATION = 'release'
SCHEMENAME = 'Taidi'
PROJECT_WORKDIR = '/Users/eric/Desktop/project/code/deploy-tool/project_src/Taidi_blue/'
PROJECT_WORKDIR_XIANSAN = '/Users/eric/Desktop/project/code/deploy-tool/project_src/Taidi_xiaoshan/'
PROJECT_WORKDIR_LANGUAN_STORY = '/Users/eric/Desktop/project/code/deploy-tool/project_src/TaidiSound/'

BRANCH = 'newCarApp'

CURRENT_SCRIPT_DIR = os.getcwd()

class ArchiveManage(object):
    """docstring for AchiveManage"""
    def __init__(self, args):
        super(ArchiveManage, self).__init__()
        scheme = args.get('scheme','')
        self.direct_upload = args.get('upload',False)
        self.direct_sendEmail = args.get('send',False)
        self.scheme = scheme
        
        if scheme == 'Taidi':
            self.project_workdir = PROJECT_WORKDIR
        elif (scheme == 'Taidi_newXiaoSan'):
            self.project_workdir = PROJECT_WORKDIR_XIANSAN
        elif (scheme == 'Taidi_newCar'):
            self.project_workdir = PROJECT_WORKDIR_XIANSAN
        elif (scheme == 'TaidiSound'):
            self.project_workdir = PROJECT_WORKDIR_LANGUAN_STORY


        self.buld_workdir = self.project_workdir + 'AutoBulid/'
    
        self.archivePath =  self.project_workdir + '%s.xcarchive' % scheme
        self.exportpath = self.buld_workdir + '%s/' % datetime.datetime.now().strftime('%Y%m%d_%H%M')
        self.workspace = self.project_workdir  + 'Taidi.xcworkspace'
        self.exportOptionsPlist = self.project_workdir + 'exportOptions.plist'
        self.ipa_path = self.exportpath + "%s.ipa" % (scheme)


    def checkoutCode(self):
        # rev = subprocess.Popen('git pull origin %s:%s' % (BRANCH, BRANCH), shell=True, stdout=subprocess.PIPE,
        #                        stderr=subprocess.PIPE)
        rev = subprocess.Popen('git pull', shell=True, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        print ''.join(rev.stdout.readlines())
        print ''.join(rev.stderr.readlines())
        #  rev = subprocess.Popen('git checkout %s' % BRANCH, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print ''.join(rev.stdout.readlines())


    def cleanArchiveFile(self):
        cleanCmd = "rm -r %s" % (self.archivePath)
        process = subprocess.Popen(cleanCmd, shell=True)
        process.wait()


    def buildWorkspace(self,workspace):
        archiveCmd = 'xcodebuild -workspace %s -scheme %s -configuration %s archive -archivePath %s -destination generic/platform=iOS' % (
            workspace, self.scheme, CONFIGURATION, self.archivePath)
        print archiveCmd
        process = subprocess.Popen(archiveCmd, shell=True)
        process.wait()

        archiveReturnCode = process.returncode
        if archiveReturnCode != 0:
            print "archive workspace %s failed" % (workspace)
            self.cleanArchiveFile()


    def exportArchive(self):
        exportCmd = "xcodebuild -exportArchive -archivePath %s -exportPath %s -exportOptionsPlist %s" % (
            self.archivePath, self.exportpath, self.exportOptionsPlist)
        process = subprocess.Popen(exportCmd, shell=True)
        (stdoutdata, stderrdata) = process.communicate()

        signReturnCode = process.returncode
        if signReturnCode != 0:
            print "export %s failed" % (self.scheme)
            return ""
        else:
            return self.ipa_path


    def uploadIpaToPgyer(self,ipaPath):
        print "ipaPath:" + ipaPath
        ipaPath = os.path.expanduser(ipaPath)
        ipaPath = unicode(ipaPath, "utf-8")
        files = {'file': open(ipaPath, 'rb')}
        headers = {'enctype': 'multipart/form-data'}
        payload = {'uKey': USER_KEY, '_api_key': API_KEY}
        print "uploading...."
        try:
            r = requests.post(PGYER_UPLOAD_URL, data=payload, files=files, headers=headers)
            if r.status_code == requests.codes.ok:
                result = r.json()
                return self.parserUploadResult(result)
            else:
                print 'HTTPError,Code:' + r.status_code
        except Exception as e:
            print e
            with open('/%s/ipaPath' % CURRENT_SCRIPT_DIR, 'w+') as f:
                f.write(ipaPath)


    def parserUploadResult(self,jsonResult):
        resultCode = jsonResult['code']
        if resultCode == 0:
            print jsonResult
            downUrl = DOWNLOAD_BASE_URL + "/" + jsonResult['data']['appShortcutUrl']
            print "Upload Success"
            print "DownUrl is:" + downUrl
            return downUrl
        else:
            print "Upload Fail!"
            print "Reason:" + jsonResult['message']
            return ''


    def getSendMailContent(self,downURL):
        publish_instruction = ''
        downURL = str(downURL)
        with open('%s/publish_instruction' % CURRENT_SCRIPT_DIR, 'r') as f:
            publish_instruction = f.read()
        publish_instruction = str(publish_instruction) + 'DownURL:%s' % downURL
        return publish_instruction


    def doUploadDirect(self,ipaPath):
        if not ipaPath:
            with open('/%s/ipaPath' % CURRENT_SCRIPT_DIR, 'r+') as f:
                ipaPath = f.readline().strip('\n')
        if ipaPath:
            downURL = uploadIpaToPgyer(ipaPath)
            publish_instruction = getSendMailContent(downURL)
            sendEmail.send_mail('iOS 新版本发布', publish_instruction)
        else:
            print 'ipaPath is not exist'




    def work(self):

        if self.direct_upload:
            self.doUploadDirect(self.direct_upload)
        elif(self.direct_sendEmail):
            downURL = self.direct_sendEmail
            publish_instruction = self.getSendMailContent(downURL)
            sendEmail.send_mail('iOS 新版本发布', publish_instruction)
        else:
            os.chdir(self.project_workdir)
            self.cleanArchiveFile()
            self.checkoutCode()
            self.buildWorkspace(self.workspace)
            path = self.exportArchive()
            if path:
                downURL = self.uploadIpaToPgyer(path)
                # downURL = 'DownUrl is:https://qiniu-storage.pgyer.com/n883'
                publish_instruction = self.getSendMailContent(downURL)
                sendEmail.send_mail('iOS 新版本发布', publish_instruction)



        

if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "u:o:d:e:s:")

    args = {}
    if len(opts) > 0:
        for op, value in opts:
            if op == '-u':
                args['upload'] = True
            if op == '-d':
                if value == 'debug':
                    CONFIGURATION = 'Debug'
            if op == '-b':
                if value:
                    BRANCH = value
            if op == '-e':
                # downURL = 'DownUrl is:https://qiniu-storage.pgyer.com/n883'
                # publish_instruction = archive_manager.getSendMailContent(value)
                # sendEmail.send_mail('iOS 新版本发布', publish_instruction)
                args['send'] = value
                print value
            if op == '-s':
                #Taidi
                args['scheme'] = value



    archive_manager = ArchiveManage(args)
    archive_manager.work()
               


    

# python archivePublish.py -u path 用参数路径上传
# python archivePublish.py -s Taidi_newXiaoSan -d debug
# python archivePublish.py -s Taidi_newXiaoSan 
# python archivePublish.py -e https://qiniu-storage.pgyer.com/7n5z 发送邮件

