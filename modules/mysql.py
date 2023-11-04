from datetime import datetime

import pymysql

db = pymysql.connect(host='localhost',
                     user='root',
                     password='123456',
                     database='qqbot')


cursor = db.cursor()


class Sql:

    @staticmethod
    async def search_draw(title):
        sql = f"SELECT * FROM `lottery_draw` WHERE is_open= 0 AND title = '{title}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def close_draw(title, win):
        sql = f'UPDATE `lottery_draw` SET `is_open` = 0,`win_qq` = "{win}"  WHERE title = "{title}"'
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def join_draw(qq, title):
        sql = f'UPDATE `lottery_draw` SET `join_qq` = CONCAT(COALESCE(`join_qq`, ""), "{qq}|") WHERE title= "{title}" AND is_open=1'
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_draw(title):
        sql = f"SELECT * FROM `lottery_draw` WHERE is_open=1 AND title = '{title}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def add_draw(qq, win_num, title, content):
        sql = f"INSERT INTO `lottery_draw` (qq, win_num, title, content) VALUES ('{qq}', {win_num}, '{title}', '{content}')"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_zuiyou(name):
        sql = f"SELECT `values` FROM `zuiyou`  WHERE name='{name}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text[0][0]

    @staticmethod
    async def update_zy_execute(content):
        sql = f"UPDATE `zuiyou` SET `values` ='{content}' WHERE name='审帖中'"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def add_zy_sty(qq):
        sql = f'UPDATE `zuiyou` SET `values` = CONCAT(COALESCE(`values`, ""), "{qq}|") WHERE name= "审帖员"'
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def update_qqlist(qq, field, content):
        sql = f"UPDATE `qq_list` SET {field}='{content}' WHERE QQ={qq}"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def add_qqlist(qq):
        sql = f"INSERT INTO `qq_list` (QQ) VALUES ({qq})"
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        return True

    @staticmethod
    async def get_qqlist(qq, field):
        sql = f"SELECT {field} FROM `qq_list` WHERE QQ={qq}"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text[0][0]

    @staticmethod
    async def get_fishlist(group, field):
        sql = f"SELECT qq,{field} FROM `touch_fish` WHERE qq_group={group} ORDER BY {field} DESC LIMIT 10 "
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def set_fish(group, qq, fish1, fish2, fish3, fish4):
        sql = f"UPDATE `touch_fish` SET 1_fish=1_fish+{fish1} , 2_fish=2_fish+{fish2} , 3_fish=3_fish+{fish3} , 4_fish=4_fish+{fish4} WHERE qq={qq} AND qq_group={group}"
        cursor.execute(sql)
        count = cursor.rowcount
        if count == 0:
            cursor.execute(f"INSERT INTO `touch_fish` (qq,qq_group) VALUES ({qq},{group})")
            cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_fish(group, qq):
        sql = f"SELECT 1_fish,2_fish,3_fish,4_fish FROM `touch_fish` WHERE  qq={qq} AND qq_group={group}"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def get_kuiping(uid):
        sql = f"SELECT * FROM `spy_screen` WHERE id = '{uid}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def del_kuiping():
        sql = f"DELETE FROM `spy_screen`"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_chatlist(name):
        sql = f"SELECT answer FROM `chat_list` WHERE question='{name}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def get_signkey(name):
        sql = f"SELECT * FROM `auto_sign` WHERE sign_name = '{name}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def set_signkey(field, text, name):
        sql = f"UPDATE `auto_sign` SET {field} = '{text}' WHERE sign_name='{name}'"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def del_kami(uid):
        sql = f"DELETE FROM `kami` WHERE uuid = '{uid}'"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def add_kami(uid, types, money, ct):
        sql = f"INSERT INTO `kami`(uuid, type, value,count) VALUES ('{uid}', '{types}', {money}, {ct})"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def change_kami(uid):
        sql = f'UPDATE `kami` SET count = count - 1 WHERE uuid = "{uid}"'
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def add_kami_qq(uid, qq):
        sql = f'UPDATE `kami` SET recharged_qq = CONCAT(COALESCE(recharged_qq, ""), "{qq}|") WHERE uuid= "{uid}"'
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_kami(uid):
        sql = f"SELECT * FROM `kami` WHERE uuid = '{uid}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def get_ranking(group, qq, field):
        sql = f"SELECT 名次 FROM (SELECT QQ, DENSE_RANK() OVER (ORDER BY {field} DESC) AS 名次 FROM `group_{group}`) as t  WHERE QQ={qq}"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def get_moneylist(group, field):
        sql = f"SELECT QQ,{field} FROM `group_{group}` ORDER BY {field} DESC LIMIT 10"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def get_vipmoney(group):
        sql = f"SELECT buy_vip_money FROM `qq_group` WHERE qq_group={group}"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text[0][0]

    @staticmethod
    async def get_blacklist(group, qq):
        sql = f"SELECT * FROM `black_list` WHERE qq_group={group} AND qq = {qq}"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def add_blacklist(group, qq):
        sql = f"INSERT INTO `black_list` VALUES ({group}, {qq})"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def del_blacklist(group, qq):
        sql = f"DELETE FROM `black_list` WHERE qq_group = '{group}' AND qq='{qq}'"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_telltime():
        sql = f"SELECT * FROM `tell_time`"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def change_mcversion(title, content):
        sql = f"UPDATE `mc_data` SET version = '{content}' WHERE name='{title}'"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_mcversion(title):
        sql = f"SELECT version FROM `mc_data` WHERE name='{title}'"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text[0][0]

    @staticmethod
    async def is_vip(group, qq):
        sql = f"SELECT vip_time FROM `group_{group}` WHERE QQ={qq}"
        cursor.execute(sql)
        db.commit()
        vip_time = cursor.fetchall()[0][0]
        now_time = datetime.timestamp(datetime.now())
        if vip_time > now_time:
            return True
        else:
            return False

    @staticmethod
    async def add_qq(group, qq):
        sql = f"INSERT INTO `group_{group}` (QQ) VALUES ({qq})"
        try:
            cursor.execute(sql)
            db.commit()
        except:
            db.rollback()
        return True

    @staticmethod
    async def update_group_field(field, content, group, qq):
        sql = f"UPDATE `group_{group}` SET {field}='{content}' WHERE QQ={qq}"
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def get_group_field(field, group, qq):  # 获取群里成员的数据
        sql = f"SELECT {field} FROM `group_{group}` WHERE QQ={qq}"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text[0][0]

    @staticmethod
    async def get_lots(num):
        sql = f"SELECT lot FROM `draw_lots` WHERE id={num}"
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text[0][0]

    @staticmethod
    async def add_group(group):
        sql = f'INSERT INTO `qq_group` (qq_group) VALUES ({group});'
        cursor.execute(sql)
        db.commit()
        return True

    @staticmethod
    async def create_table(group):  # 建表
        sql = f"""CREATE TABLE IF NOT EXISTS `group_{group}`  (
  `QQ` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'QQ号',
  `Money` int NOT NULL DEFAULT 0 COMMENT '蜜桃币',
  `bank_money` int NOT NULL DEFAULT 0 COMMENT '银行金额',
  `sign_time` date NOT NULL DEFAULT '1970-01-01' COMMENT '签到时间',
  `even_sign` int NOT NULL DEFAULT 0 COMMENT '连续签到天数',
  `total_sign` int NOT NULL DEFAULT 0 COMMENT '总共签到天数',
  `vip_time` bigint NOT NULL DEFAULT 0 COMMENT '会员到期时间，时间戳',
  `treasure_data` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL COMMENT '宝物数据： ’ | ‘ 分开',
  `purview` int NOT NULL DEFAULT 0 COMMENT '权限 0：群员，1：管理员，2：主人，3：创始人',
  `interest_time` date NOT NULL DEFAULT '1970-01-01' COMMENT '领取利息时间',
  `say_num` int NULL DEFAULT 0 COMMENT '发言数量',
  PRIMARY KEY (`QQ`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;"""
        try:
            cursor.execute(sql)
            db.commit()
        except:
            return False
        return True

    @staticmethod
    async def change_group_open(group, is_open):
        sql = f"UPDATE qq_group SET is_open={is_open} WHERE qq_group={group}"
        cursor.execute(sql)
        db.commit()
        count = cursor.rowcount
        if count == 0:
            return False
        return True

    @staticmethod
    async def change_group(group, key, value):
        sql = f"UPDATE qq_group SET {key}='{value}' WHERE qq_group={group}"
        cursor.execute(sql)
        db.commit()
        count = cursor.rowcount
        return True

    @staticmethod
    async def is_open(group, field="is_open"):  # 是否初始化过 是否开启本群
        sql = f'SELECT {field} FROM `qq_group` WHERE qq_group={group}'
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        if len(text) == 1 and text[0][0] == 1:
            return True
        return False

    @staticmethod
    async def select_open(field, key, value):
        sql = f'SELECT {field} FROM `qq_group` WHERE {key}={value}'
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        return text

    @staticmethod
    async def is_founder(qq):  # 是否是创始人
        sql = f'SELECT QQ FROM `founder` WHERE QQ={qq}'
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        if len(text) != 0:
            return True
        return False

    @staticmethod
    async def is_qq_exist(group, qq):  # qq是否在表中
        sql = f'SELECT * FROM `group_{group}` WHERE QQ={qq}'
        cursor.execute(sql)
        db.commit()
        text = cursor.fetchall()
        if len(text) != 0:
            return True
        return False

    @staticmethod
    async def change_money(group, qq, name, money, operation):
        """
        更改表中数值
        Args:
            group:群号
            qq:qq号
            name:字段名
            money:金额数
            operation:+或-
        Returns:
            无
        """
        sql = f'UPDATE `group_{group}` SET {name} = {name} {operation} {money} WHERE QQ={qq}'
        cursor.execute(sql)
        db.commit()
        return

    @staticmethod
    async def set_money(group, qq, name, money):
        sql = f'UPDATE `group_{group}` SET {name} = "{money}" WHERE QQ={qq}'
        cursor.execute(sql)
        db.commit()
        return


Sql = Sql()
