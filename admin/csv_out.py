
import csv

from weibo_data.models import *
def run():
    weibo_datas = WeiboData.objects.all()
    weibo_users = WbUser.objects.all()
    uid2weibo_user = {w.uid: w for w in weibo_users}
    head = ['微博id', '用户id', '昵称', '性别', '生日', '所在地', '简介', '注册时间', '关注数', '粉丝数', '微博数', '头像',
            '联系信息', '教育信息', '工作信息', '用户tags', '用户等级', '微博内容', '回复数', '评论数', '点赞数', 'url', '发布时间']
    all_data = []
    all_data.append(head)
    for weibo_data in weibo_datas:
        if weibo_data.uid not in uid2weibo_user:
            continue
        weibo_user = uid2weibo_user[weibo_data.uid]
        line = [
            weibo_data.weibo_id,
            weibo_data.uid,
            weibo_user.name,
            {0: '未知', 1: "男", 2: "女"}.get(weibo_user.gender),
            weibo_user.birthday,
            weibo_user.location,
            weibo_user.description,
            weibo_user.register_time,
            weibo_user.follows_num,
            weibo_user.fans_num,
            weibo_user.wb_num,
            weibo_user.head_img,
            weibo_user.contact_info,
            weibo_user.education_info,
            weibo_user.work_info,
            weibo_user.tags,
            weibo_user.level,
            weibo_data.weibo_cont,
            weibo_data.repost_num,
            weibo_data.comment_num,
            weibo_data.praise_num,
            weibo_data.weibo_url,
            weibo_data.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        ]
        all_data.append(line)

    with open("all_data.csv", 'w') as out:
        csv_write = csv.writer(out, dialect='excel')
        for line in all_data:
            print(line)
            csv_write.writerow(line)
