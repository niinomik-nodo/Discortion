import os
from datetime import datetime

import settings
from keep_alive import keep_alive

import discord
from notion_client import Client

# TODO
import sys
import logging
logger = logging.getLogger()


# TODO
def set_handler():

    # get date
    now = datetime.now()
    save_file_name = str(now)[:10].replace('-', '') + '.log'  # YYYYMMDD.log

    # get save dir
    save_dir = '/var/log/notion_api'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    save_dir_name =  os.path.join(save_dir, save_file_name)

    # set logger level
    logger.setLevel(logging.ERROR)

    # set error handler
    formatter = logging.Formatter('%(asctime)s %(lineno)s %(message)s', '%Y/%m/%d %H:%M:%S')
    fh = logging.FileHandler(filename=save_dir_name, encoding='utf-8')
    fh.setLevel(logging.ERROR)
    fh.setFormatter(formatter)
    logger.addHandler(fh)


def get_message(message):
    # TODO
    try:
        err_flg = False
        command = message.content
        if "/curr" in command:
            get_messemger_name = message.author.display_name
            user_name = get_messemger_name.split("_")[0]
            database_id_list = settings.database_id_list
            database_id = database_id_list[get_messemger_name.split("_")[1]]
            curr_number = command.split(" ")[1]
            return user_name, database_id, curr_number, err_flg
    except Exception as e:
        print("exception e(___DEBGU___): ", e)
        get_messemger_name = message.author.display_name
        err_message = 'command: {}, error message: {}, username: {}'.format(command, e, get_messemger_name)
        # print("err_message(___DEBUG___): ", err_message)
        # print("type(err_message): ", type(err_message))
        logger.error(err_message)

        err_flg = True
        return get_messemger_name, '', '', err_flg
        # os.system("kill 1")
        # sys.exit()


# def transform_three_digit_number(curr_num):
#     if len(curr_num) == 1:
#         new_curr_num = "00" + curr_num
#     elif len(curr_num) == 2:
#         new_curr_num = "0" + curr_num
#     else:
#         new_curr_num = curr_num
#     return new_curr_num


def main():
    # Discord_Token
    TOKEN = os.environ['DISCORD_KEY']
    # TOKEN = 'MTA5ODEwNDI1OTkyNjU3MzA3Ng.G7pCDo.e16s9QEh33C6ELIvdE4JGBRtbTrv1zpZNze7MM'

    # Notion_token
    NOTION_TOKEN = os.environ['NOTION_KEY']
    # NOTION_TOKEN = 'secret_013tQKTmEmdOOWcBgcPBTKNN3wAOzgQhTSkN2t63M2U'

    # Initializing Notion Client
    notion = Client(auth=NOTION_TOKEN)

    # Discord Channel ID
    CHANNEL_ID = "1098841750077968435"

    # 接続に必要なオブジェクトを生成
    client = discord.Client(intents=discord.Intents.all())

    # TODO
    # set error handler
    set_handler()

    # 起動時に動作する処理
    @client.event
    async def on_ready():
        # 起動したらターミナルにログイン通知が表示される
        print('ログインしました')

    # 発言時に実行されるイベントハンドラを定義
    @client.event
    async def on_message(message):
        # コマンドに対応するデータを取得して表示
        # username, database_id, curr_number = get_message(message)
        username, database_id, curr_number, err_flg = get_message(message)

        if err_flg:
            return

        # TODO
        try:
            # Check if the message is from the desired channel
            if message.channel.id == int(CHANNEL_ID):

                # if curr_num is Not Three Digit Number, Change Three Digit Number.
                # TODO
                # trans_curr_no = transform_three_digit_number(curr_number)
                trans_curr_no = curr_number.zfill(3)

                # Check if the username retrieved from Discord exists in Notion's database.
                results = notion.databases.query(
                    **{
                        "database_id": database_id,
                        "filter": {
                            "property": "名前",
                            "title": {
                                "contains": username,
                            },
                        },
                    }).get("results")

            if not results:
                # Notion Page Properties
                create_page_properties = {
                    '名前': {
                        'title': [{
                            'text': {
                                'content': username
                            }
                        }]
                    },
                    'カリキュラムNo': {
                        'rich_text': [{
                            'text': {
                                'content': trans_curr_no
                            }
                        }]
                    },
                    '更新日': {
                        'date': {
                            'start': datetime.now().strftime('%Y-%m-%d')
                        }
                    }
                }

                # Adding the page to Notion Database
                notion.pages.create(parent={'database_id': database_id},
                                    properties=create_page_properties)
                print("クリエイト成功")

            # Check if the username retrieved from Discord exists in Notion's database.
            else:
                page_id = results[0]["id"]

                update_page_properties = {
                    'カリキュラムNo': {
                        'rich_text': [{
                            'text': {
                                'content': trans_curr_no
                            }
                        }]
                    },
                    '更新日': {
                        'date': {
                            'start': datetime.now().strftime('%Y-%m-%d')
                        }
                    }
                }

                # Update to the property to Notion Database
                notion.pages.update(page_id=page_id,
                                    properties=update_page_properties)

                # notion.pages.create(parent={'database_id': DATABASE_ID}, properties=create_page_properties)
                print("アップデート成功")

        except Exception as e:
            print("exception e: ", e)
            command = message.content
            get_messemger_name = message.author.display_name
            err_message = 'command: {}, error message: {}, username: {}'.format(command, e, get_messemger_name)
            logger.error(err_message)
            # os.system("kill 1")
            # sys.exit()

    keep_alive()
    # connect to Discord server
    try:
        client.run(TOKEN)
    except:
        # os.system("kill 1")
        sys.exit()


if __name__ == "__main__":
    main()