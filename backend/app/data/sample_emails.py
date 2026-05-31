"""演示邮件（15 封）—— 覆盖核心场景，供新用户快速体验。

完整 100 封测试集见 test_emails_100.py（仅开发者评估用）。
日期使用相对表达，由规则引擎动态解析。
"""

SAMPLE_EMAILS = [
    # -- 明确任务 (8 封) --
    {"id":"demo-01","name":"周报提交","sender":"主管 manager@example.com","subject":"请明天下午前提交本周工作周报","body":"请明天下午18:00前提交本周工作周报，重点说明项目进展、风险和下周计划。","expected_should_create":True},
    {"id":"demo-02","name":"客户故障","sender":"客户 support@example.com","subject":"系统登录异常需要今天处理","body":"客户反馈系统登录一直失败，麻烦今天下班前定位原因并回复处理结果。","expected_should_create":True},
    {"id":"demo-03","name":"培训报名","sender":"培训中心 training@example.com","subject":"下周三前完成数据安全培训报名","body":"请在下周三前填写报名表并确认是否参加线下考试。","expected_should_create":True},
    {"id":"demo-04","name":"项目例会","sender":"项目秘书 secretary@example.com","subject":"本周五项目例会材料准备","body":"请本周五15:00参加项目例会，并提前准备各自模块的进展说明。","expected_should_create":True},
    {"id":"demo-05","name":"合同确认","sender":"法务 legal@example.com","subject":"合同条款确认","body":"请明天上午前确认附件合同中的付款条款，如有问题请直接批注后回复。","expected_should_create":True},
    {"id":"demo-06","name":"客户回访","sender":"销售总监 sales@example.com","subject":"重点客户回访安排","body":"麻烦尽快联系A公司客户，确认试用反馈并更新CRM记录。","expected_should_create":True},
    {"id":"demo-07","name":"论文修改","sender":"导师 li@lab.edu","subject":"论文审稿意见修改","body":"请在下周内完成第二轮审稿意见修改，重点补充实验对照组和消融分析。","expected_should_create":True},
    {"id":"demo-08","name":"账单确认","sender":"财务 finance@example.com","subject":"账单已生成请确认付款信息","body":"本月账单已生成，请今天确认付款信息是否正确。如有问题请直接回复。","expected_should_create":True},

    # -- 明确非任务 (5 封) --
    {"id":"demo-09","name":"验证码","sender":"安全中心 security@example.com","subject":"登录验证码","body":"你的验证码是384921，5分钟内有效。若非本人操作请忽略。","expected_should_create":False},
    {"id":"demo-10","name":"系统维护","sender":"IT运维 it@example.com","subject":"系统维护通知","body":"系统将在周六凌晨进行维护，期间可能短暂不可用。本邮件仅为通知无需处理。","expected_should_create":False},
    {"id":"demo-11","name":"游戏活动","sender":"游戏活动 promo@example.com","subject":"限时活动登录领取补给箱","body":"后天前登录游戏可领取补给箱。该奖励为限时活动福利。","expected_should_create":False},
    {"id":"demo-12","name":"自动回复","sender":"auto-reply@example.com","subject":"自动回复我已收到你的邮件","body":"我目前正在休假，回来后会尽快处理。本邮件为自动回复。","expected_should_create":False},
    {"id":"demo-13","name":"广告促销","sender":"优惠 newsletter@shop.example.com","subject":"限时优惠会员专享折扣","body":"本周商城促销活动开启，点击链接领取优惠券。本邮件为广告订阅内容。","expected_should_create":False},

    # -- 陷阱 (2 封，规则易误判) --
    {"id":"demo-14","name":"转发他人任务","sender":"同事 colleague@example.com","subject":"Fwd: 会议纪要摘录","body":"纪要里提到市场部需要在明天前提交活动预算。这个事项由市场部负责，我只是转发给你了解背景。","expected_should_create":False,"expected_rule_may_fail":True},
    {"id":"demo-15","name":"条件安全提醒","sender":"安全中心 security@example.com","subject":"账户安全提醒","body":"如果不是你本人操作请尽快修改密码；如果是你本人操作可以忽略本提醒。","expected_should_create":False,"expected_rule_may_fail":True},
]
