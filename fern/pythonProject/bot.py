import discord
from discord.ext import commands
from discord import app_commands
from typing import Union

# 권한을 활성화 (리액션 감지)
intents = discord.Intents.default()
intents.reactions = True  # 리액션 감지 활성화
intents.members = True  # 멤버 관련 이벤트 활성화
intents.messages = True  # 메시지 관련 이벤트 활성화
intents.message_content = True  # 메시지 내용을 읽고 쓸 수 있는 권한

bot = commands.Bot(command_prefix='/', intents=intents)

MESSAGE_ID = 1341841622920597608  # 메시지 ID
MANAGER_USER_ID = 875257348178980875 # 서버 관리자 아이디
sentId = [1125042802124927007, 931800387164454912, 1251068997428842559] # 보냈던 ID
channel = bot.get_channel(1341586962385211402)

formURL = "https://forms.office.com/Pages/ResponsePage.aspx?id=DQSIkWdsW0yxEjajBLZtrQAAAAAAAAAAAAN__jCBoBhURTBVWVFXOVNJSTNRVVA2NjFSSjZURERLUi4u"

@bot.event
async def on_ready():
    print("로그인 성공!")
    global channel
    # 봇이 준비되었을 때 채널을 한 번 확인
    channel = bot.get_channel(1341586962385211402)
    print(channel)
    await bot.tree.sync()
    for command in bot.tree.get_commands():
        print(f"Command: {command.name}")

@bot.event
async def on_raw_reaction_add(payload):
    """ 특정 메시지에 반응이 추가될 때 이벤트를 발생시킴 """

    # 봇이 반응한 경우 무시
    if payload.user_id == bot.user.id:
        return

    # 반응한 메시지 ID가 특정 메시지와 일치할 때
    if payload.message_id == MESSAGE_ID:
        # 유저 ID 출력
        print(f"이모지에 반응한 사용자 ID: {payload.user_id}")
        if(not payload.user_id in sentId):
            try:
                # 사용자 ID로 DM 보내기
                user = await bot.fetch_user(payload.user_id)
                manager = await bot.fetch_user(MANAGER_USER_ID)
                await user.send("엘프 클럽에 가입해주셔서 감사합니다!\n"
                                "24시간 이내에 관리자 검토 후 '인증됨' 역할을 부여해 드리겠습니다.")
                await manager.send("관리자님! @" + user.name + "에게 DM을 보냈습니다! 확인해 주세요." )
                print(f"DM을 {user.name}에게 성공적으로 보냈습니다.")
                sentId.append(payload.user_id)
            except discord.Forbidden:
                print(f"{user.name}에게 DM을 보낼 수 없습니다. DM 수신 설정을 확인해주세요.")
            except Exception as e:
                print(f"DM을 보내는 중 오류 발생: {e}")

@bot.event
async def on_member_join(member):
    print(channel)
    """사용자가 서버에 들어왔을 때 실행되는 이벤트"""
    print(member.name + "님이 서버에 입장하셨습니다!")
    manager = await bot.fetch_user(MANAGER_USER_ID)
    await channel.send(f"{member.display_name}님 엘프 클럽에 오신 것을 환영합니다!\n"
                       "규칙을 읽고 :white_check_mark:이모지에 반응을 추가해 주신다면 관리자 검토 후 '인증됨' 역할을 부여해 드리겠습니다.")
    await manager.send("관리자님! @" + member.display_name + "님이 서버에 입장하셨습니다! 확인해 주세요.")

@bot.tree.command(name="게임-초대-보내기", description="친구에게 게임 초대를 전송합니다.")
@app_commands.describe(
    게임="초대할 게임의 이름을 입력하세요. (목록에 표시되는 게임은 서버에서 지원하는 게임입니다.)",
    초대인원="초대 인원의 수를 입력하세요. ('1명' 또는 '2명 이상')",
    초대대상="초대할 대상을 입력하세요. (서버에서 지원하고, 초대 인원이 '2명 이상'이라면 비워두세요.)",
    남길메시지="친구에게 남길 메시지를 입력하세요. (없다면 비워두세요.)"
)
async def invite(interaction: discord.Interaction, 게임: str, 초대인원: str, 초대대상: Union[discord.User, discord.Role] = None, 남길메시지: str = "없음"):
    user_id = interaction.user.id  # 명령어를 호출한 사람의 ID
    user_display_name = interaction.user.display_name # 명령어를 호출한 사람의 표시 이름
    channel_id = bot.get_channel(interaction.channel.id) # 호출한 채널의 ID
    if( 게임 in [
        "Grand Theft Auto V",
        "PUBG BATTLEGROUNDS",
        "Minecraft",
        "Roblox",
        "League of Legends",
        "Valorant",
        "Test"
    ] and 초대인원 == "2명 이상"):
        초대대상 = discord.utils.get(interaction.guild.roles, name=게임)
        members = [member.id for member in 초대대상.members]
        if(user_id in members):
            members.remove(user_id)
        for i in members:
            i = await bot.fetch_user(i)
            await i.send(user_display_name + "님이  " + 게임 + "의 초대를 보냈습니다. 엘프 클럽을 확인해 보시는 건 어떨까요?\n" +
                         user_display_name + "님이 남긴 메시지: \"" + 남길메시지 + "\"")
    else:
        send_user_id = await bot.fetch_user(초대대상.id)
        await send_user_id.send(user_display_name + "님이  " + 게임 + "의 초대를 보냈습니다. 엘프 클럽을 확인해 보시는 건 어떨까요?\n" +
                     user_display_name + "님이 남긴 메시지: \"" + 남길메시지 + "\"")

    if(not 초대대상 == None):
        await interaction.channel.send("초대 전송이 완료되었어요.")
        await channel_id.send("# 초대 전송 완료!\n" + 게임 + "의 초대가 정상적으로 전송이 완료되었습니다. 친구들을 기다려 보세요!\n 사용: " + user_display_name)
        print(user_display_name + "님이 " + 게임 + "을/를 " + str(초대대상) + "에게 초대를 보냈습니다!")
    else:
        print("초대 보내기를 실패했습니다.")
        await interaction.channel.send("초대 전송에 실패했어요.")
        await channel_id.send("# 초대 전송 실패\n초대가 전송이 되지 않았어요ㅜ.ㅜ 서버에서 지원하지 않는 게임이거나, 초대 인원이 1명이라면 초대 대상을 입력하세요.\n 사용: " + user_display_name)

@invite.autocomplete("초대인원")
async def 초대인원_autocomplete(interaction: discord.Interaction, current: str):
    choices = ["1명", "2명 이상"]
    return [
        discord.app_commands.Choice(name=choice, value=choice)
        for choice in choices if current.lower() in choice.lower()
    ]

@invite.autocomplete("게임")
async def 초대인원_autocomplete(interaction: discord.Interaction, current: str):
    choices = [
        "Grand Theft Auto V",
        "PUBG BATTLEGROUNDS",
        "Minecraft",
        "Roblox",
        "League of Legends",
        "Valorant"
    ]
    return [
        discord.app_commands.Choice(name=choice, value=choice)
        for choice in choices if current.lower() in choice.lower()
    ]
@bot.tree.command(name="모집-정보", description="운영진 모집 정보를 확인합니다.")
async def button_command(interaction: discord.Interaction):
    # 링크 버튼 만들기
    button = discord.ui.Button(label="운영진 신청", style=discord.ButtonStyle.link, url=formURL)
    view = discord.ui.View()
    view.add_item(button)

    # 버튼이 포함된 메시지 전송
    await interaction.response.send_message("# 운영진 모집 안내 \n"
                                            "모집 기간 : 2025-03-05 - 2025-03-14 10일간\n"
                                            "모집 인원 : 0명\n"
                                            "아래 버튼을 사용하여 신청해 주세요.\n"
                                            "*\"/모집-정보\"를 사용하여 이 문구를 출력할 수 있습니다.*", view=view)
    print("운영진 모집 정보가 사용되었습니다.")

bot.run('-')
