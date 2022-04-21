# Author: leeyiding(乌拉)
# Date: 2021-08-12
# Link: 
# Version: 0.0.24
# UpdateDate: 2022-1-28 11:15
# UpdateLog: 去除发布文章功能

import requests,json,time,random
from utils import logger,config,logDir,cleanLog
from notify import send

class SeresCheckin():
    def __init__(self,cookie,baseData,draw):
        self.cookie = cookie
        self.baseData = baseData
        self.draw = draw
        # self.commentList = ['👍','👏','🧡','😀','赞','日常水贴','积分+1','努力攒积分','帖子不错','good']
        self.checkinNum = 1
        self.read15sNum = 15
        self.using10mNum = 1
        self.likeNum = 5
        self.shareNum = 5
        # self.commentNum = 10
        # self.postNum = 5

    def postApi(self,service,option,function,postData={}):
        headers = {
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'User-Agent': 'okhttp-okgo/jeasonlzy',
            'APPACCESSTOKEN': self.cookie,
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '106',
            'Host': 'app.seres.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
        }
        postData.update(self.baseData)
        response = requests.post('https://app.seres.cn/api/{}/app/{}/{}'.format(service,option,function), headers=headers, data=postData)
        return response.json()

    def postApi2(self,service,option,function,params):
        headers = {
            'token': self.cookie,
            'time': str(int(time.time())),
            'Content-Type': 'application/x-www-form-urlencoded',
            'APPACCESSTOKEN': self.cookie,
            'Content-Length': '0',
            'Host': 'app.seres.cn',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/4.9.0',
        }
        headers.update(self.baseData)
        response = requests.post('https://app.seres.cn/api/{}/app/{}/{}'.format(service,option,function), headers=headers, params=params)
        return response.json()
    
    def postApi3(self,service,option,function):
        if option == 'checkin':
            Referer = 'http://adminapp.seres.cn/h5/checkin.html?token={}&topBarHeight=35'.format(self.cookie)
            data = {}
        elif option == 'lottery':
            Referer = 'http://adminapp.seres.cn/h5/lottery/01.html?lotterySn=JGG01&loginToken={}'.format(self.cookie)
            data = {
                'lotterySn': 'JGG01'
            }
        headers = {
            'Host': 'app.seres.cn',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'Sec-Fetch-Mode': 'cors',
            'Origin': 'http://adminapp.seres.cn',
            'APPACCESSTOKEN': self.cookie,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Redmi K30 5G Build/RKQ1.200826.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045714 Mobile Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
            'X-Requested-With': 'cn.seres',
            'Sec-Fetch-Site': 'cross-site',
            'Referer': Referer,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        params = (
            ('_ts', int(round(time.time()*1000))),
        )
        response = requests.post('https://app.seres.cn/api/{}/app/{}/{}'.format(service,option,function), headers=headers, params=params, data=data)
        return response.json()
    
    def checkCookie(self):
        userInfo = self.postApi('user', 'me', 'get-me-center-data')
        if userInfo['code'] == '4001':
            logger.error('用户{} Cookie无效'.format(i+1))
            send("SERES账号失效通知",'用户{} Cookie已失效'.format(i+1))
            return False
        self.nickname = userInfo['value']['nickname']
        points = userInfo['value']['points']
        logger.info('用户{}登陆成功，当前积分{}'.format(self.nickname,points))
        
    def checkTaskStatus(self):
        pageIndex = 0 
        while True:
            params = (
                ('pageIndex', str(pageIndex)),
            )
            getPointResult = self.postApi2('user', 'point', 'transactions', params)
            totalPages = getPointResult['value']['totalPages']
            for point in range(len(getPointResult['value']['list'])):
                if getPointResult['value']['list'][point]['time'] < today:
                    return
                content = getPointResult['value']['list'][point]['content']
                if content == '每日签到奖励':
                    self.checkinNum -= 1
                elif content == '每日浏览动态奖励':
                    self.read15sNum -= 1
                elif content == '每日在线10分钟奖励':
                    self.using10mNum -= 1
                elif content == '每日点赞奖励':
                    self.likeNum -= 1
                elif content == '每日分享动态奖励':
                    self.shareNum -= 1
                # elif content == '每日评论奖励':
                #     self.commentNum -= 1
                # elif content == '每日动态奖励':
                #     self.postNum -= 1
            if pageIndex < totalPages:
                pageIndex += 1
            else:
                return

    def checkin(self):
        # 1积分
        logger.info('今日剩余签到次数{}'.format(self.checkinNum))
        for i in range(self.checkinNum):
            checkinResult = self.postApi('user', 'me', 'checkin')
            if checkinResult == True:
                logger.info('签到获得{}积分'.format(checkinResult['value']))
            else:
                logger.info(checkinResult['message'])
        getHomeDataResult = self.postApi3('user','checkin','get-home-data')
        if getHomeDataResult['success'] == False:
            return
        logger.info('已连续签到天数：{}，已累积签到天数{}'.format(getHomeDataResult['value']['continuousCheckins'],getHomeDataResult['value']['totalCheckinPoints']))
        if getHomeDataResult['value']['rewardProduct'] != None:
            logger.info('获得连续签到奖品：【{}】'.format(getHomeDataResult['value']['rewardProduct']['name']))

    def getPost(self):
        postData = {
            'parentType': '1',
            'sort': '1',
            'pageIndex': '0',
            'pageSize': '20'
        }
        getPostResult = self.postApi('community', 'post', 'search', postData)
        if getPostResult['success'] == True:
            logger.info('共发现{}篇文章'.format(getPostResult['value']['pageSize']))
            return getPostResult['value']['list']

    def readPost(self):
        # 浏览动态1积分*15 点赞1积分*5 分享动态1积分*5 评论1积分*10
        logger.info('今日剩余浏览动态次数{}'.format(self.read15sNum))
        logger.info('今日剩余点赞次数{}'.format(self.likeNum))
        # logger.info('今日剩余评论次数{}'.format(self.commentNum))
        logger.info('今日剩余分享次数{}'.format(self.shareNum))
        if (self.read15sNum > 0) or (self.likeNum > 0) or (self.shareNum > 0):
            post = self.getPost()
        # 浏览动态
        for i in range(max(self.read15sNum,self.likeNum,self.shareNum)):
            postData = {
                'postId': post[i]['postId']
            }
            logger.info('阅读 {} 动态【{}】'.format(post[i]['userNickname'],post[i]['content']))
            self.postApi('community', 'post', 'get-details-data', postData)
            time.sleep(15)
            awardResult = self.postApi('user', 'point', 'add-for-post-reading-15s', postData)
            if awardResult['success'] == True:
                logger.info('阅读获得{}积分'.format(awardResult['value']['amount']))
            # 点赞
            if self.likeNum > 0 and post[i]['liked'] == False:
                postData['cancel'] = 'false'
                likeResult = self.postApi('community', 'post', 'like', postData)
                if likeResult['success'] == True:
                    logger.info(likeResult['message'])
                    postData = {
                        'code': 'first_like'
                    }
                    self.postApi('user', 'point', 'add-for-first-rule', postData)
                    self.likeNum -= 1
            # 评论
            # if self.commentNum > 0:
            #     postData = {
            #         'content': random.choice(self.commentList),
            #         'objectType': '0',
            #         'objectId': post[i]['postId']
            #     }
            #     commentResult = self.postApi('community', 'comment', 'submit', postData)
            #     if commentResult['success'] == True:
            #         logger.info(commentResult['message'])
            #         commentId = commentResult['value']
            #         postData = {
            #             'code': 'first_comment'
            #         }
            #         self.postApi('user', 'point', 'add-for-first-rule', postData)
            #         self.commentNum -= 1
            #         time.sleep(2)
            #         # 删评
            #         postData = {
            #             'commentId': commentId
            #         }
            #         delCommentResult = self.postApi('community', 'comment', 'delete-mine', postData)
            #         if delCommentResult['success'] == True:
            #             logger.info(delCommentResult['message'])
            # 分享
            if self.shareNum > 0:
                postData = {
                    'content': '每日分享动态奖励',
                    'postId': post[i]['postId']
                }
                awardResult = self.postApi('user', 'point', 'add-for-daily-share', postData)
                if awardResult['success'] == True:
                    logger.info('分享获得{}积分'.format(awardResult['value']['amount']))
                self.shareNum -= 1
            time.sleep(2)

    def submitPost(self):
        # 发表动态 5*2积分
        logger.info('今日发表动态次数{}'.format(self.postNum))
        for i in range(self.postNum):
            postData = {
                'content': ' '
            }
            # 发帖
            submitPostResult = self.postApi('community','post','submit',postData)
            logger.info(submitPostResult['message'])
            if submitPostResult['success'] == False:
                continue
            postId = submitPostResult['value']['postId']
            time.sleep(2)
            # 删帖
            postData = {
                'id': postId
            }
            deletePostResult = self.postApi('community','post','delete',postData)
            logger.info(deletePostResult['message'])
            time.sleep(2)
            
    def online10min(self):
        # 在线10分钟 1积分
        logger.info('今日剩余领取在线10分钟奖励次数{}'.format(self.using10mNum))
        if (int(time.time()) * 1000) < (today + 10 * 60 * 1000):
            logger.info('未到00:10，暂不领取奖励')
            return
        for i in range(self.using10mNum):
            awardResult = self.postApi('user', 'point', 'add-for-using-10min')
            if awardResult['success'] == True:
                logger.info('在线10分钟获得{}积分'.format(awardResult['value']['amount']))
    
    def lottery(self):
        # 获取免费抽奖机会
        addLotteryTryResult =  self.postApi3('user','lottery','add-one-try')
        # 查询机会
        getLotteryDetailsResult =  self.postApi3('user','lottery','get-details')
        if getLotteryDetailsResult == False:
            return False
        todayRestTries = getLotteryDetailsResult['value']['todayRestTries']
        freeRestTries = getLotteryDetailsResult['value']['freeRestTries']
        if self.draw == '' or self.draw == False:
            restTries = freeRestTries
            logger.info('默认不使用积分抽奖，否则请将draw设置为true')
        else:
            restTries = todayRestTries
        logger.info('今日剩余抽奖次数：{}'.format(restTries))
        for i in range(restTries):
            logger.info('开始第{}次抽奖'.format(i+1))
            lotteryResult = self.postApi3('user','lottery','try-lottery')
            if lotteryResult['success'] == False:
                continue
            if lotteryResult['value']['rewardName'] == None:
                logger.info('抽中💨')
            else:
                logger.info('运气爆棚抽中{}'.format(lotteryResult['value']['rewardName']))
                send("SERES中奖通知","账号【{}】运气爆棚，抽中{}".format(self.nickname,lotteryResult['value']['rewardName']))
            time.sleep(5)
        
    def main(self):
        if self.checkCookie() == False:
            return False
        self.checkTaskStatus()
        self.checkin()
        self.readPost()
        # self.submitPost()
        self.online10min()
        # self.lottery()

if __name__ == '__main__':
    userNum = len(config['cookie'])
    logger.info('共{}个账号'.format(userNum))
    today = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime(int(time.time()))), "%Y-%m-%d"))) * 1000

    for i in range(userNum):
        logger.info('开始账号{}'.format(i+1))
        cookie = config['cookie'][i]
        user = SeresCheckin(cookie,config['baseData'],config['draw'])
        user.main()
    cleanLog(logDir)
    