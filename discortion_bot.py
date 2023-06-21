import os
from datetime import datetime

# import settings
from settings import database_id_list
from keep_alive import keep_alive

import discord
from notion_client import Client

import sys
import logging
logger = logging.getLogger()


error_dict = {
    "annaounce": {
        "command": {
            "/curr": "想定されていないフォーマットのコマンドを検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・コマンドの最初は「/curr」で始めてください。\n"\
                     "・「/curr」と数字の間にスペースを入れてください。\n\n"\
                     "(例) /curr 001",

            "digit": "想定されていないフォーマットのコマンドを検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・3桁0埋めの数字で入力してください。\n\n"\
                     "(例) /curr 001",

        },
        "user": {
            "digit": "想定されていないフォーマットの名前を検知しました。\n"\
                     "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                     "・5桁0埋めの数字で設定してください。\n\n"\
                     "(例) テスト太郎_00001\n\n"\
                     "ユーザ名の設定方法は下記URLからご確認ください。\n"\
                     "https://setup-lab.net/discord-nickname-change/",

            "_": "想定されていないフォーマットの名前を検知しました。\n"\
                 "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                 "・氏名と数字の間は「_」で設定してください。\n\n"\
                 "(例) テスト太郎_00001\n\n"\
                 "ユーザ名の設定方法は下記URLからご確認ください。\n"\
                 "https://setup-lab.net/discord-nickname-change/",

            "nodigit": "想定されていないフォーマットの名前を検知しました。\n"\
                       "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                       "・氏名の後にご自身のDBに対応する5桁0埋めの数値を設定してください。\n\n"\
                       "(例) テスト太郎_00001\n\n"\
                       "ユーザ名の設定方法は下記URLからご確認ください。\n"\
                       "https://setup-lab.net/discord-nickname-change/",

            "nickname": "discord上に表示させる名前を「サーバープロフィール」に設定してください。\n\n"\
                        "ユーザ名の設定方法は下記URLからご確認ください。\n"\
                        "https://setup-lab.net/discord-nickname-change/",

        },
        "both": "コマンド、および名前双方に想定されていないフォーマットを検知しました。\n"\
                "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                "(例)\n"\
                "・コマンド: /curr 001\n"\
                "・名前: テスト太郎_00001\n\n"\
                "ユーザ名の設定方法は下記URLからご確認ください。\n"\
                "https://setup-lab.net/discord-nickname-change/",

        "unknown": "不明なエラーを検知しました。\n"\
                   "下記をご確認の上、再度コマンドを入力してください。\n\n"\
                   "(例)\n"\
                   "・コマンド: /curr 001\n"\
                   "・名前: テスト太郎_00001\n\n"\
                   "エラーが解消されない場合、運営にお問い合わせください。",

    },
    "message": {
        "command": {
            "/curr": "[/curr ] could not found.",
            "digit": "Integer Missing.",
        },
        "user": {
            "digit": "Integer Missing.",
            "_": "Underscore has not detected.",
            "nodigit": "Name has no digit.",
            "nickname": "Ncikname and Displayname did not match.",
        },
        "both": "command and name detect error.",
        "unknown": "Unknown error has detected.",
    }
}

# set error handler
# get save dir
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


# check and get error message, announce
# explicit registrate info
def get_message(message):

    try:

        # init error messages
        error_message = None
        error_annaounce = None

        # get message info
        command = message.content  # command statement
        get_messemger_name = message.author.display_name  # displaied user name in chat

        # check error
        err_message_command, err_announce_command = check_command(command)
        err_message_username, err_annaounce_username = check_user(get_messemger_name)

        # no error
        if not ( bool(err_message_command) | bool(err_message_username)):

            user_name = get_messemger_name.split("_")[0]  # explicit full name from displaied user name
            database_id = database_id_list[get_messemger_name.split("_")[1]]  # explicit database id from displaied user name
            curr_number = command[6:].zfill(3)  # explicit curriculum number from command statement

            return user_name, database_id, curr_number, error_annaounce

        # any error
        else:

            # command and name error
            if bool(err_message_command) & bool(err_message_username):
                error_message = error_dict["message"]["both"]
                error_annaounce = error_dict["annaounce"]["both"]

            # command error
            elif bool(err_message_command):
                error_message = err_message_command
                error_annaounce = err_announce_command

            # name error
            elif bool(err_message_username):
                error_message = err_message_username
                error_annaounce = err_annaounce_username

            raise ValueError(error_message)

    except Exception as e:

        # get error log
        print("exception e(___DEBGU___): ", e)
        err_line = 'command: {}, error message: {}, username: {}'.format(command, e, get_messemger_name)
        logger.error(err_line)

        # unknown error
        if error_annaounce is None:
            error_annaounce = error_dict["annaounce"]["unknown"]

        return get_messemger_name, '', '', error_annaounce


# TODO
def check_command(command):
    err_message = None
    err_annaounce = None
    if command[:6] != '/curr ':
        err_message = error_dict["message"]["command"]["/curr"]
        err_annaounce = error_dict["annaounce"]["command"]["/curr"]
    elif not command[6:].isdigit():
        err_message = error_dict["message"]["command"]["digit"]
        err_annaounce = error_dict["annaounce"]["command"]["digit"]
    return err_message, err_annaounce


# TODO
def check_user(messemger_name):
    err_message = None
    err_annaounce = None
    if (not messemger_name[-1].isdigit()) | (messemger_name[-1] == "_"):
        err_message = error_dict["message"]["user"]["nodigit"]
        err_annaounce = error_dict["annaounce"]["user"]["nodigit"]
    elif not messemger_name[-5:].isdigit():
        err_message = error_dict["message"]["user"]["digit"]
        err_annaounce = error_dict["annaounce"]["user"]["digit"]
    elif messemger_name[-6] != '_':
        err_message = error_dict["message"]["user"]["_"]
        err_annaounce = error_dict["annaounce"]["user"]["_"]
    return err_message, err_annaounce


def main():
    # Discord_Token
    # TOKEN = os.environ['DISCORD_KEY']
    # TOKEN = 'MTA5ODEwNDI1OTkyNjU3MzA3Ng.G7pCDo.e16s9QEh33C6ELIvdE4JGBRtbTrv1zpZNze7MM'
    TOKEN = "MTExMzA5NjUwMDA4NDQ5MDMyMQ.GT9WTH.TcHOQQ9sRQkgNE1lBTNe0sCpyd9P9Q2m_CVSkg"

    # Notion_token
    # NOTION_TOKEN = os.environ['NOTION_KEY']
    NOTION_TOKEN = 'secret_013tQKTmEmdOOWcBgcPBTKNN3wAOzgQhTSkN2t63M2U'

    # Initializing Notion Client
    notion = Client(auth=NOTION_TOKEN)

    # Discord Channel ID 
    # CHANNEL_ID = "1098841750077968435"  # daily report
    # CHANNEL_ID = "1098157558885273621"
    CHANNEL_ID = "1119239857751986227"  # bot_bot

    # 接続に必要なオブジェクトを生成
    client = discord.Client(intents=discord.Intents.all())

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

        # check commanded user
        # (ignore process for bot and Administrator)
        if (message.author != client.user) & (message.author.display_name[-3:] != "@運営"):

            # コマンドに対応するデータを取得して表示
            username, database_id, curr_number, err_announce = get_message(message)

            # send error message to user in chat
            if bool(err_announce):
                await message.channel.send(err_announce)
                return

            try:
                # Check if the message is from the desired channel
                if message.channel.id == int(CHANNEL_ID):

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
                                    # 'content': trans_curr_no
                                    'content': curr_number
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
                                    # 'content': trans_curr_no
                                    'content': curr_number
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
                err_line = 'command: {}, error message: {}, username: {}'.format(command, e, get_messemger_name)
                logger.error(err_line)
        else:
            return

    keep_alive()
    # connect to Discord server
    try:
        client.run(TOKEN)
    except:
        sys.exit()


if __name__ == "__main__":
    main()
