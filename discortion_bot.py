import os
from datetime import datetime

import settings
from keep_alive import keep_alive

import discord
from notion_client import Client


def get_message(message):
    command = message.content
    if "/curr" in command:
        get_messemger_name = message.author.display_name
        user_name = get_messemger_name.split("_")[0]
        database_id_list = settings.database_id_list
        database_id = database_id_list[get_messemger_name.split("_")[1]]
        curr_number = command.split(" ")[1]
    return user_name, database_id, curr_number


def transform_three_digit_number(curr_num):
    if len(curr_num) == 1:
        new_curr_num = "00" + curr_num
    elif len(curr_num) == 2:
        new_curr_num = "0" + curr_num
    else:
        new_curr_num = curr_num
    return new_curr_num


def main():
    # Discord_Token
    TOKEN = os.environ['DISCORD_KEY']

    # Notion_token
    NOTION_TOKEN = os.environ['NOTION_KEY']

    # Initializing Notion Client
    notion = Client(auth=NOTION_TOKEN)

    # Discord Channel ID
    CHANNEL_ID = "1098841750077968435"

    # 接続に必要なオブジェクトを生成
    client = discord.Client(intents=discord.Intents.all())

    # 起動時に動作する処理
    @client.event
    async def on_ready():
        # 起動したらターミナルにログイン通知が表示される
        print('ログインしました')

    # 発言時に実行されるイベントハンドラを定義
    @client.event
    async def on_message(message):
        # コマンドに対応するデータを取得して表示
        username, database_id, curr_number = get_message(message)

        # Check if the message is from the desired channel
        if message.channel.id == int(CHANNEL_ID):

            # if curr_num is Not Three Digit Number, Change Three Digit Number.
            trans_curr_no = transform_three_digit_number(curr_number)

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

    keep_alive()
    # connect to Discord server
    try:
        client.run(TOKEN)
    except:
        os.system("kill 1")


if __name__ == "__main__":
    main()
