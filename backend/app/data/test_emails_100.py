"""100 封真实办公/科研环境测试邮件 —— 仅开发者评估用，不面向用户。

每封带 expected_should_create 标记，部分带 expected_rule_may_fail。
日期全部使用相对表达（今天/明天/后天/下周/月底）。
"""
TEST_EMAILS_100 = [
    # ═══ 明确工作任务 (30 封) — should_create=True ═══

    # -- 周报/报告类 --
    {"sender":"主管 manager@company.com","subject":"请明天下午前提交本周工作周报","body":"请明天下午18:00前提交本周工作周报，重点说明项目进展、风险和下周计划。","expected_should_create":True},
    {"sender":"项目经理 pm@company.com","subject":"本周五项目例会材料准备","body":"请本周五15:00参加项目例会，并提前准备各自模块的进展说明。","expected_should_create":True},
    {"sender":"总监 director@company.com","subject":"季度总结报告提交","body":"请在下周三前完成Q2季度总结报告，包含关键指标、项目里程碑和风险分析。","expected_should_create":True},
    {"sender":"HR hr@company.com","subject":"绩效考核自评填写","body":"请在本周五前完成本季度绩效考核自评表格，登录HR系统填写并提交。","expected_should_create":True},

    # -- 客户/商务类 --
    {"sender":"客户 support@client.com","subject":"系统登录异常需要紧急处理","body":"客户反馈系统登录一直失败，麻烦今天下班前定位原因并回复处理结果。","expected_should_create":True},
    {"sender":"销售总监 sales@company.com","subject":"重点客户回访安排","body":"麻烦尽快联系A公司客户，确认试用反馈并更新CRM记录。","expected_should_create":True},
    {"sender":"客户经理 account@company.com","subject":"试用反馈跟进","body":"麻烦下周三联系客户确认试用反馈，并把结果更新到CRM。","expected_should_create":True},
    {"sender":"客户 client@partner.com","subject":"合同付款条款确认","body":"请明天上午前确认附件合同中的付款条款，如有问题请直接批注后回复。","expected_should_create":True},
    {"sender":"商务 bd@company.com","subject":"供应商报价对比","body":"请后天前完成三家供应商的报价对比，整理成表格发我。","expected_should_create":True},
    {"sender":"客户 service@client.com","subject":"售后问题跟进","body":"客户反馈安装包无法打开，麻烦跟进一下并给客户回复。","expected_should_create":True},

    # -- 审批/签字类 --
    {"sender":"法务 legal@company.com","subject":"合同条款确认","body":"请明天上午前确认附件合同中的付款条款和违约责任，如无问题请回复确认。","expected_should_create":True},
    {"sender":"财务 finance@company.com","subject":"采购申请审批","body":"请在今天下班前审批采购申请单，金额超过预算需要你特别确认。","expected_should_create":True},
    {"sender":"行政 admin@company.com","subject":"请假审批","body":"张三申请下周一至周三请假，需要你作为直属主管审批。","expected_should_create":True},
    {"sender":"财务 finance@company.com","subject":"出差报销审批","body":"请在明天前审批我的出差报销单，附上了所有发票扫描件。","expected_should_create":True},

    # -- 会议/日程 --
    {"sender":"秘书 secretary@company.com","subject":"项目例会准备材料","body":"下周一项目例会，请准备以下材料：上周进展、本周计划、需要协调的事项。","expected_should_create":True},
    {"sender":"外部 partner@other.com","subject":"技术交流会议安排","body":"请在本周内确认下周三技术交流会议的时间和参会人员名单并回复。","expected_should_create":True},
    {"sender":"培训 training@company.com","subject":"数据安全培训报名","body":"请在下周三前完成数据安全培训报名，确认是否参加线下考试。","expected_should_create":True},

    # -- 文档/内容 --
    {"sender":"市场 marketing@company.com","subject":"产品发布公告审核","body":"请今天内审核产品发布公告稿件，修改意见请直接在文档中批注。","expected_should_create":True},
    {"sender":"同事 colleague@company.com","subject":"协助完善方案","body":"我在准备客户方案，麻烦你帮忙补充技术架构部分的内容，明天前给我。","expected_should_create":True},
    {"sender":"产品 product@company.com","subject":"需求文档评审","body":"请在下周二前完成需求文档评审，重点关注接口设计和数据迁移方案。","expected_should_create":True},

    # -- 行政/后勤 --
    {"sender":"行政 admin@company.com","subject":"办公用品申领","body":"请在月底前提交下季度办公用品申领清单，各部门统一汇总。","expected_should_create":True},
    {"sender":"IT it@company.com","subject":"设备更换申请","body":"请明天前在IT系统中提交老旧电脑更换申请，注明配置需求和业务影响。","expected_should_create":True},
    {"sender":"HR hr@company.com","subject":"新员工入职手续","body":"请在本周内为新同事张三办理入职手续，包括开通账号、分配设备和安排导师。","expected_should_create":True},

    # -- 紧急/故障 --
    {"sender":"监控 monitor@company.com","subject":"生产环境告警","body":"生产环境CPU使用率超过90%，请立即排查，可能是新上线功能导致。","expected_should_create":True},
    {"sender":"客户 support@client.com","subject":"客户投诉系统登录异常","body":"客户投诉系统登录异常，请今天下班前处理并回复排查结果。","expected_should_create":True},

    # -- 账单/确认 --
    {"sender":"财务 finance@company.com","subject":"账单已生成请确认","body":"本月账单已生成，请今天确认付款信息是否正确。如有问题请直接回复。","expected_should_create":True},
    {"sender":"系统系统 noreply@system.com","subject":"请今天完成实名认证","body":"请今天完成实名认证，否则明天开始将无法提交审批流程。","expected_should_create":True},

    # -- 低信息量 --
    {"sender":"行政 admin@company.com","subject":"请明天前上传附件","body":"请明天前上传附件。邮件里没有说明具体附件名称，需要你确认后再处理。","expected_should_create":True},
    {"sender":"客户 client@example.com","subject":"尽快回复方案意见","body":"麻烦尽快看一下我给你们的方案，有什么修改意见尽快回复我。","expected_should_create":True},
    {"sender":"同事 colleague@company.com","subject":"帮忙看看这段代码","body":"帮我review一下这个PR里的代码逻辑有没有问题，今天有空的话帮忙看看。","expected_should_create":True},

    # ═══ 科研/学术 (15 封) — should_create=True ═══

    {"sender":"导师 li@university.edu","subject":"论文修改意见","body":"请在下周内完成第二轮审稿意见修改，重点补充实验对照组和消融分析。","expected_should_create":True},
    {"sender":"期刊 editor@journal.org","subject":"审稿邀请","body":"邀请你审阅一篇投稿论文，请在两周内提交审稿意见。","expected_should_create":True},
    {"sender":"会议 committee@conference.org","subject":"论文录用通知及修改要求","body":"你的论文已被接收，请按评审意见修改并在月底前提交最终版本和版权转让表。","expected_should_create":True},
    {"sender":"导师 li@university.edu","subject":"项目预算提交","body":"请后天前提交实验室下季度项目预算，需包含设备采购和差旅费用明细。","expected_should_create":True},
    {"sender":"合作者 collab@otherlab.edu","subject":"联合实验数据","body":"请在本周内把你那边的实验数据整理好发给我，我们需要合并分析。","expected_should_create":True},
    {"sender":"基金委 nsfc@nsfc.gov.cn","subject":"基金申请书修改","body":"基金申请书需要补充可行性分析，请在周五前完成修改并提交。","expected_should_create":True},
    {"sender":"学生 student@university.edu","subject":"毕设中期检查","body":"请在下周安排毕设中期检查的时间，需要提前准备PPT和进度报告。","expected_should_create":True},
    {"sender":"课题组 group@lab.edu","subject":"组会报告安排","body":"下周三组会由你做进展报告，请准备20分钟的PPT，重点讲近期实验数据。","expected_should_create":True},
    {"sender":"实验室 manager@lab.edu","subject":"设备采购申请","body":"请在月底前整理实验室需要采购的设备清单，包括型号、数量和预算估计。","expected_should_create":True},
    {"sender":"学院 office@university.edu","subject":"教学评估填写","body":"请在本周五前完成本学期教学评估，登录教务系统匿名填写。","expected_should_create":True},
    {"sender":"导师 li@university.edu","subject":"国际会议投稿","body":"下周一截稿的ICML论文请尽快润色摘要，同时按会议模板调整格式，完成后发我终审。","expected_should_create":True},
    {"sender":"学生 student@university.edu","subject":"助教作业批改","body":"请在本周末前批改完第三章作业并录入成绩，有问题学生需要下周反馈。","expected_should_create":True},
    {"sender":"合作方 partner@research.org","subject":"合作协议签署","body":"请今天打印合作协议一式三份签字盖章后寄出，地址见附件。","expected_should_create":True},
    {"sender":"教务 dean@university.edu","subject":"课程大纲更新","body":"请在下学期开始前完成课程大纲更新，提交至教务系统审核。","expected_should_create":True},
    {"sender":"图书 librarian@university.edu","subject":"数据库试用反馈","body":"请在本周内试用新订购的数据库，填写使用反馈表。","expected_should_create":True},

    # ═══ IT/系统通知 (15 封) — should_create=False ═══

    {"sender":"IT运维 it@company.com","subject":"系统维护通知","body":"系统将在周六凌晨2:00-4:00进行维护，期间可能短暂不可用。本邮件仅为通知，无需处理。","expected_should_create":False},
    {"sender":"IT it@company.com","subject":"密码即将过期提醒","body":"你的系统密码将在7天后过期，请在方便时登录系统更新密码。","expected_should_create":False},
    {"sender":"IT it@company.com","subject":"办公软件版本更新","body":"办公软件已发布新版本，增加了若干功能改进。更新将在下次启动时自动安装，无需手动操作。","expected_should_create":False},
    {"sender":"安全 security@company.com","subject":"安全补丁已部署","body":"本周安全补丁已部署完毕，无需额外操作。如发现异常请及时反馈。","expected_should_create":False},
    {"sender":"IT it@company.com","subject":"VPN证书更新通知","body":"VPN证书将于月底到期，届时会自动更新，无需手动操作。","expected_should_create":False},
    {"sender":"IT it@company.com","subject":"网络维护完成","body":"昨晚的网络维护已完成，所有服务已恢复正常。如仍有连接问题请联系IT。","expected_should_create":False},
    {"sender":"IT it@company.com","subject":"新打印机配置说明","body":"三楼新打印机已安装完毕，连接方式见附件说明文档。","expected_should_create":False},
    {"sender":"IT it@company.com","subject":"存储空间清理提醒","body":"你的OneDrive存储空间已使用80%，建议清理不需要的文件。这只是提醒，不是强制要求。","expected_should_create":False},
    {"sender":"系统 noreply@system.com","subject":"登录提醒","body":"检测到你的账号在新设备上登录。如果是你本人操作，可以忽略本提醒。","expected_should_create":False},
    {"sender":"系统 noreply@system.com","subject":"账号绑定确认","body":"你已成功绑定手机号，后续可通过手机验证码登录。","expected_should_create":False},
    {"sender":"IT it@company.com","subject":"新员工账号开通","body":"张三的企业账号已开通，邮箱和VPN均已配置完毕。","expected_should_create":False},
    {"sender":"系统 noreply@hr.com","subject":"工资条已发布","body":"本月工资条已发布在HR系统中，请登录查看。本邮件为自动发送。","expected_should_create":False},
    {"sender":"HR hr@company.com","subject":"社保基数调整通知","body":"根据最新政策，下月起社保缴费基数将调整。详情查看附件政策文件。","expected_should_create":False},
    {"sender":"行政 admin@company.com","subject":"停车位分配结果","body":"本季度停车位分配结果已出，请查看附件名单。","expected_should_create":False},
    {"sender":"系统 noreply@system.com","subject":"系统升级完成","body":"昨晚的系统升级已顺利完成，新功能包括报表导出和批量操作，详见更新日志。","expected_should_create":False},

    # ═══ 非任务/营销/垃圾 (25 封) — should_create=False ═══

    {"sender":"newsletter@tech.com","subject":"AI行业周报","body":"本期内容包含模型发布、融资动态和行业观察。你收到这封邮件是因为订阅了周报。","expected_should_create":False},
    {"sender":"marketing@shop.com","subject":"限时优惠会员专享折扣","body":"本周商城促销活动开启，点击链接领取优惠券。本邮件为广告订阅内容。","expected_should_create":False},
    {"sender":"security@company.com","subject":"登录验证码","body":"你的验证码是384921，5分钟内有效。若非本人操作，请忽略。","expected_should_create":False},
    {"sender":"hr@company.com","subject":"员工满意度调查","body":"诚邀你参加本年度员工满意度调查，点击链接填写问卷。参与为自愿性质。","expected_should_create":False},
    {"sender":"news@company.com","subject":"公司新闻简报","body":"本期简报汇总了本月公司重要动态和行业新闻，供各位了解。","expected_should_create":False},
    {"sender":"hr@company.com","subject":"欢迎新同事","body":"欢迎张三加入我们团队，他将负责后端开发工作。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"events@company.com","subject":"年会报名通知","body":"年会将于下月举行，有意参加的同事务必在月底前填写报名表。","expected_should_create":False},
    {"sender":"admin@company.com","subject":"食堂菜单更新","body":"下周食堂菜单已更新，新增了川菜窗口。","expected_should_create":False},
    {"sender":"hr@company.com","subject":"健康体检通知","body":"年度健康体检将于下月开始，请关注后续具体安排通知。","expected_should_create":False},
    {"sender":"calendar@company.com","subject":"已接受团队团建聚餐","body":"你已接受此邀请。活动时间本周五18:30。本邮件为自动通知。","expected_should_create":False},
    {"sender":"auto-reply@partner.com","subject":"自动回复我已收到你的邮件","body":"我目前正在休假，回来后会尽快处理。本邮件为自动回复。","expected_should_create":False},
    {"sender":"receipt@payment.com","subject":"您的购买收据","body":"这是您的购买收据。如果不是本人购买请尽快联系平台客服。本邮件为交易凭证。","expected_should_create":False},
    {"sender":"logistics@express.com","subject":"您的快递正在派送中","body":"您的快递预计今天下午送达，请保持电话畅通。如有问题请联系快递员。","expected_should_create":False},
    {"sender":"Steam noreply@steampowered.com","subject":"您最近的Steam社区市场交易","body":"这封邮件用于确认您最近的社区市场交易。如非本人操作请访问Steam帐户安全页面。","expected_should_create":False},
    {"sender":"Steam noreply@steampowered.com","subject":"您已成功为Steam钱包充值","body":"您的Steam钱包已充值成功。本邮件为交易收据无需回复。","expected_should_create":False},
    {"sender":"Steam noreply@steampowered.com","subject":"愿望单游戏现已推出","body":"您愿望单中的游戏现已在Steam上推出，点击查看商店页面。","expected_should_create":False},
    {"sender":"promo@game.com","subject":"限时活动登录领取补给箱","body":"后天前登录游戏可领取补给箱。该奖励为限时活动福利，领取与否不影响账户使用。","expected_should_create":False},
    {"sender":"Steam support@steampowered.com","subject":"已收到您的退款申请","body":"我们已收到您的退款申请正在处理中。在处理完成前无需再次提交或回复本邮件。","expected_should_create":False},
    {"sender":"finance@company.com","subject":"报销申请已通过","body":"你的差旅报销申请已审批通过，款项将在3个工作日内到账。本邮件为系统自动发送。","expected_should_create":False},
    {"sender":"noreply@bank.com","subject":"信用卡账单已生成","body":"您的信用卡账单已生成，请登录网银查看详情。","expected_should_create":False},
    {"sender":"events@conference.org","subject":"会议日程更新","body":"附件是最新的会议日程安排，包含各分会场主题和嘉宾信息。供参考。","expected_should_create":False},
    {"sender":"secretary@company.com","subject":"项目例会会议纪要","body":"附件是今天项目例会会议纪要，供大家查阅。本邮件无需回复。","expected_should_create":False},
    {"sender":"wiki@company.com","subject":"知识库更新通知","body":"知识库中关于部署流程的文档已更新，新增了Docker部署章节。","expected_should_create":False},
    {"sender":"hr@company.com","subject":"新福利政策介绍","body":"公司新增了弹性工作制和补充商业保险两项福利，详情见附件政策文件。","expected_should_create":False},
    {"sender":"info@community.org","subject":"社区活动周报","body":"本周社区活动汇总：技术沙龙、开源贡献日、线上答疑。感兴趣的可以参加。","expected_should_create":False},

    # ═══ 陷阱/边界 (15 封) — expected_rule_may_fail=True ═══

    {"sender":"同事 colleague@company.com","subject":"Fwd: 会议纪要摘录","body":"纪要里提到市场部需要在明天前提交活动预算。这个事项由市场部负责，我只是转发给你了解背景。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"wiki@company.com","subject":"报销流程说明文档","body":"这份文档说明了团队通常如何提交报销材料、如何审批预算、以及如何在系统中更新记录，供新人了解流程，不需要你做什么。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"promo@shop.com","subject":"会员福利领取提醒","body":"月底前登录活动页面即可领取会员福利礼包，数量有限先到先得。这是营销活动不是工作任务。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"security@company.com","subject":"账户安全提醒","body":"如果不是你本人操作请尽快修改密码；如果是你本人操作可以忽略本提醒。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"receipt@payment.com","subject":"您的购买收据","body":"这是您的购买收据。如果不是本人购买请尽快联系平台客服。本邮件为交易凭证。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"events@game.com","subject":"周末双倍经验活动开启","body":"本周末登录游戏可享受双倍经验加成。请在周六前登录领取首日奖励，该奖励需要手动在活动页面提交领取申请。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"同事 colleague@company.com","subject":"方案初稿","body":"这是我整理的方案初稿，你有空可以看看，有什么想法随时沟通。没有明确截止时间。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"noreply@system.com","subject":"系统通知请及时更新个人信息","body":"请在方便时登录系统更新你的个人联系方式。这不是强制要求只是一个定期提醒。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"HR hr@company.com","subject":"组织架构调整通知","body":"公司组织架构将于下月调整，请各部门主管在明天前提交本部门人员调整建议。你作为普通员工无需操作。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"客户 client@company.com","subject":"表扬信","body":"感谢你们团队的高效服务，特别是张三在项目中的出色表现。我只是想表达感谢，不需要回复。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"财务 finance@company.com","subject":"发票已开具","body":"你申请的增值税专用发票已开具，电子版见附件。如信息有误请今天内联系财务修改，否则视为确认无误。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"经理 manager@company.com","subject":"团队建设活动意见征集","body":"我们计划下个月组织团建活动，请大家在方便时提供建议。没有强制要求。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"同事 colleague@company.com","subject":"请教一个问题","body":"你知道那个数据分析平台怎么导出PDF报告吗？我找了半天没找到，你有空帮我看看。","expected_should_create":False,"expected_rule_may_fail":True},
    {"sender":"合作方 partner@other.com","subject":"会议纪要确认","body":"附件是上周会议的纪要，请确认内容是否准确。如有需要补充的请告知。","expected_should_create":True,"expected_rule_may_fail":True},
    {"sender":"产品 product@company.com","subject":"用户反馈汇总","body":"这是本周的用户反馈汇总，其中登录慢的问题影响较多用户，建议安排处理。","expected_should_create":True,"expected_rule_may_fail":True},
]
