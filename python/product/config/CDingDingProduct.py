from framework.config.CDingDing import *
class CDingDingProduct(CDingDing):
    version = '0.0.0'
    groups = {
        'All' : {
            'webhook':'https://oapi.dingtalk.com/robot/send?access_token=6f00f283da82d7b29674e8130dc42de77c2428d3c829b4f60a531860ed311853',
            'secret':'SEC9b969d5859a2c59635169921ada53a4cbf681ed7be7670f97b17c9913628d2d7',
        }
    }