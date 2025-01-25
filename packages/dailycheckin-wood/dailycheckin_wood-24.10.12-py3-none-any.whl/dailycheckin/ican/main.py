import json
import os
import requests
import urllib3
import random
import time
from datetime import datetime

from dailycheckin import CheckIn

urllib3.disable_warnings()


class ICan(CheckIn):
    name = "ICAN"

    def __init__(self, check_item: dict):
        self.check_item = check_item
        self.base_url = 'https://ican.sinocare.com'

    def update_token(self, refresh_token):
        url = f'{self.base_url}/api/sino-archives/v1/user/info'
        headers = {'Sino-Auth': refresh_token}
        response = requests.get(url=url, headers=headers, verify=False)  # 禁用 SSL 证书验证
        print(f'update_token:  {response.status_code}')
        status_code = response.status_code
        return status_code

    def sign(self, access_token):
        '''
           签到
        '''
        url = f'{self.base_url}/api/sino-member/signRecord/sign'
        headers = {'Sino-Auth': access_token}
        response = requests.get(url=url, headers=headers, verify=False)  # 禁用 SSL 证书验证
        # print(json.loads(response.text))
        return [{"name": "ICAN", "value": json.loads(response.text)['msg']}]

    def record_uric_acid(self, access_token):
        '''
            记录尿酸
        '''
        msg = []
        url = f'{self.base_url}/api/sino-health/ua/save?familyUserId='
        headers = {'Sino-Auth': access_token, 'Content-Type': 'application/json'}
        for i in range(0, 3):
            data = {
                "mode": 1,
                "deviceSn": "",
                "detectionIndicatorsId": "2",
                "detectionChannel": "1",
                "detectionUnit": "μmol/L",
                "detectionTime": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                "detectionWay": 1,
                "remark": "",
                "sex": 1,
                "result": {
                    "ua": {
                        "val": random.randrange(260, 450),
                        "unit": "μmol/L",
                        "sex": 1
                    }
                }
            }
            response = requests.post(url=url, headers=headers, data=json.dumps(data), verify=False)

            if response.status_code != 200:
                return [{"name": "ICAN", "value": f"第{i}次记录尿酸失败"}]

            msg.append({"name": f"ICAN 第{i}次记录尿酸", "value": "成功"})
            time.sleep(2)
        return msg

    def record_diet(self, access_token):
        '''
              记录饮食
        '''
        headers = {'Sino-Auth': access_token, 'Content-Type': 'application/json'}
        food_url = f'{self.base_url}/api/sino-knowledge/v1/food-items-info/page-app'
        diet_url = f'{self.base_url}/api/sino-health/v1/diet-record/save-or-update'
        data = {"current": 1, "size": 10, "isHot": 1}
        response = requests.post(url=food_url, headers=headers, data=json.dumps(data), verify=False)
        if response.status_code != 200:
            return [{"name": "ICAN", "value": "获取食物列表失败"}]

        msg = []
        response_data = json.loads(response.text)
        for i in range(0, 4):
            random_number = random.randrange(0, 9)
            foods = response_data["data"]["records"]
            data = {
                "uploadType": "0",
                "platformType": 1,
                "dietTypeName": "午餐",
                "dietTime": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                "dietType": 5,
                "dataSource": 1,
                "remark": "",
                "isSocial": 0,
                "messageContent": "",
                "energyIntake": 16,
                "carbohydrate": 2,
                "fat": 0,
                "protein": 0,
                "detailReqList": [
                    {
                        "dietProjectId": foods[random_number]["id"],
                        "dietProjectName": foods[random_number]["dietName"],
                        "dietRecordEnergy": random.randrange(100, 800),
                        "dietEnergyIntake": 2,
                        "dietRecordNum": 16,
                        "carbohydrate": 2,
                        "fat": 0,
                        "protein": 0,
                        "dietUnit": "克",
                        "uploadType": "0",
                        "photoUrl": foods[random_number]["dietPictures"],
                        "type": 2
                    }
                ]
            }
            response = requests.post(url=diet_url, headers=headers, data=json.dumps(data), verify=False)

            if response.status_code != 200:
                return [{"name": "ICAN", "value": f"第{i}次记录饮食失败"}]

            msg.append({"name": f"ICAN 第{i}次记录饮食", "value": "成功"})
            time.sleep(2)
        return msg

    def record_blood_sugar(self, refresh_token):
        '''
            记录血糖
        '''
        msg = []
        headers = {'Sino-Auth': refresh_token, 'Content-Type': 'application/json'}
        url = f'{self.base_url}/api/sino-health/detectiondata/addDetectionData?familyUserId='
        for i in range(0, 4):
            data = {
                "mode": 1,
                "detectionIndicatorsId": 1,
                "detectionChannel": 1,
                "detectionTime": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                "detectionWay": 1,
                "detectionWayType": 0,
                "detectionWaySource": 0,
                "remark": "",
                "isSocial": 0,
                "image": "",
                "messageContent": "",
                "result": {
                    "glucose": {
                        "val": f'{random.uniform(5, 6.5):.1f}',
                        "unit": "mmol/L",
                        "timeCode": "5",
                        "timeCodeName": "午餐后"
                    }
                },
                "version": 1
            }
            response = requests.post(url=url, headers=headers, data=json.dumps(data), verify=False)
            if response.status_code != 200:
                return [{"name": "ICAN", "value": "记录血糖失败"}]
            msg.append({"name": f"ICAN 第{i}次记录饮食", "value": "成功"})
            time.sleep(5)
        return msg

    def get_question(self, refresh_token):
        '''
            答题
        '''
        msg = []
        headers = {'Sino-Auth': refresh_token, 'Content-Type': 'application/json'}
        url = f'{self.base_url}/api/sino-social/dailyQuestion/getQuestion'

        response = requests.get(url=url, headers=headers, verify=False)
        if response.status_code != 200:
            print(response)
            return [{"name": "ICAN", "value": "获取题目失败"}]
        response_data = json.loads(response.text)
        options=response_data['data']['options']


    def post_a_comment(self, refresh_token):
        msg = []
        time_= int(datetime.now().timestamp()*1000)
        headers = {'Sino-Auth': refresh_token, 'Content-Type': 'application/json'}
        get_by_score_url = f'{self.base_url}/api/sino-social/messageinformation/get-by-score'
        url = f'{self.base_url}/api/sino-social/reviewinformation/add'
        data = {
            "current": 1,
            "size": 10,
            "createTime": time_,
            "isTop": ""
        }
        response = requests.post(url=get_by_score_url, headers=headers, data=json.dumps(data), verify=False)
        if response.status_code != 200:
            print(response)
            return [{"name": "ICAN", "value": "获取评论失败"}]
        response_data = json.loads(response.text)
        for i in range(0, 3):
            data = {
                "messageContentId": f"{response_data['data']['records'][i]['id']}",
                "messageSource": "2",
                "reviewType": 1,
                "reviewContent": "学习了",
                "specialSign": 1,
                "replyAccountId": f"{response_data['data']['records'][i]['accountId']}",
                "topicSubjectId": response_data['data']['records'][i]['topicType'],
                "contentType": 1
            }
            response = requests.post(url=url, headers=headers, data=json.dumps(data), verify=False)
            if response.status_code != 200:
                return [{"name": "ICAN", "value": "发布评论失败"}]
            msg.append({"name": f"ICAN 第{i}次发布评论", "value": "成功"})
            time.sleep(5)
        return msg

    def main(self):
        refresh_token = self.check_item.get("Sino-Auth")
        # status_code = self.update_token(refresh_token)
        # if status_code != 200:
        #     return [{"name": "ICAN", "value": "token 过期"}]
        msg = self.sign(refresh_token)
        print(msg)
        msg = self.record_blood_sugar(refresh_token)
        print(msg)
        msg = self.record_diet(refresh_token)
        print(msg)
        msg = self.record_uric_acid(refresh_token)
        print(msg)
        msg = self.post_a_comment(refresh_token)
        print(msg)
        msg = self.record_active(refresh_token)
        print(msg)
        msg = self.record_drug(refresh_token)
        print(msg)
        # msg=self.get_question(refresh_token)
        # print(msg)
        return msg

    def record_active(self, refresh_token):
        msg = []
        headers = {'Sino-Auth': refresh_token, 'Content-Type': 'application/json'}
        url = f'{self.base_url}/api/sino-health/sportrecord/addSportRecordNew'
        for i in range(0, 3):
            data = [{
                "sportPictures": "https://sino-cloud-base.oss-cn-hangzhou.aliyuncs.com/fileupload-develop/20210107/5a497a63e508fcc5eb97d702a13eb2dd.png",
                "consumeEnergy": 153,
                "dataSource": 1,
                "remark": "",
                "sportProjectId": "604f4ab83d7f102ccc166242",
                "sportProjectName": "走路(慢)",
                "sportRecordCompany": "分钟",
                "sportRecordEnergy": 60,
                "sportTime": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S"),
                "sportEnergy": "153",
                "sportUnit": "分钟",
                "sportUnitNum": 60,
                "platformType": 3}]
            response = requests.post(url=url, headers=headers, data=json.dumps(data), verify=False)
            if response.status_code != 200:
                return [{"name": "ICAN", "value": "记运动失败"}]
            msg.append({"name": f"ICAN 第{i}次记运动", "value": "成功"})
            time.sleep(5)
        return msg
        pass

    def record_drug(self, refresh_token):
        msg = []
        headers = {'Sino-Auth': refresh_token, 'Content-Type': 'application/json'}
        url = f'{self.base_url}/api/sino-health/v1/drug-record/save-drug-record-new'
        for i in range(0, 3):
            time_ = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "platformType": 9,
                "saveRecord": 1,
                "dataSource": 1,
                "list": [
                    {"drugId": "5dbb9bad0c07bb0008df65b4",
                     "drugName": "消渴丸",
                     "drugNum": 1,
                     "drugBrand": "消渴丸 含格列本脲",
                     "drugTime": time_,
                     "drugUnit": "丸",
                     "drugSpec": "2.5mg/10丸",
                     "type": 1,
                     "isSupplement": 1,
                     "minute": "",
                     "period": 4,
                     "remark": "",
                     "id": "5dbb9bad0c07bb0008df65b4"}],
                "drugTime": (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")}
            response = requests.post(url=url, headers=headers, data=json.dumps(data), verify=False)
            if response.status_code != 200:
                return [{"name": "ICAN", "value": "记用药失败"}]
            msg.append({"name": f"ICAN 第{i}次记用药", "value": "成功"})
            time.sleep(5)
        return msg
        pass


if __name__ == "__main__":
    with open(
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json"),
            encoding="utf-8",
    ) as f:
        datas = json.loads(f.read())
    _check_item = datas.get("ICAN", [])[0]
    print(f'账户 {_check_item}')
    print(ICan(check_item=_check_item).main())
