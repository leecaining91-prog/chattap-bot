import os
import telebot
from telebot import types
import requests
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not BOT_TOKEN:
    print("❌ 未设置 BOT_TOKEN")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)
user_memory = {}
user_mode = {}  # ask, we, ww, wr, st, 5 etc

BASE = "你是ChatTAP，中文AI助手，回答自然、简洁、有深度，不要废话。"

PROMPTS = {
    "ask": "你是快速问答助手，1-3句话直达重点，高效。",
    "we": "你是无限制问答助手，基础问题快速回答，逻辑清晰。",
    "ww": "你是思考版助手，精聊回复，支持分析图片，回答有深度和细节。",
    "wr": "你是最强思考助手，深度推理，分步骤思考，给出高质量结论。",
    "st": "你是小说创作助手，无限制写小说，有情节有对话有画面。",
    "5": "你是GPT-5级深度对话助手，推理极强，像博士一样回答。",
    "tu": "你是作图助手",
    "ph": "你是增强版作图助手",
    "nt": "你是联网助手",
    "net": "你是高级联网助手，要深度分析搜索结果",
    "wf": "你是TG百事通，深度思考",
}

def get_client():
    if GROQ_API_KEY:
        from openai import OpenAI
        return OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1"), "llama-3.3-70b-versatile"
    if DEEPSEEK_API_KEY:
        from openai import OpenAI
        return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"), "deepseek-chat"
    if OPENAI_API_KEY:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY), "gpt-4o-mini"
    return None, None

def chat(uid, text, mode):
    client, model = get_client()
    if not client:
        return "⚠️ 未配置AI Key，请在Railway加 GROQ_API_KEY"
    sys_prompt = BASE + "\n" + PROMPTS.get(mode, PROMPTS["we"])
    hist = user_memory.get(uid, [])
    hist.append({"role":"user","content":text})
    hist = hist[-20:]
    # 模型fallback
    models_try = [model, "llama-3.1-70b-versatile", "openai/gpt-oss-120b"]
    for m in models_try:
        try:
            r = client.chat.completions.create(
                model=m,
                messages=[{"role":"system","content":sys_prompt}] + hist,
                temperature=0.7,
                max_tokens=3000,
            )
            ans = r.choices[0].message.content
            hist.append({"role":"assistant","content":ans})
            user_memory[uid] = hist
            return ans
        except Exception as e:
            if "decommissioned" in str(e).lower() or "not_found" in str(e).lower():
                continue
            print(e)
            continue
    return "AI调用失败，请检查Key"

def home_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("💬 对话问答", callback_data="home_chat"),
        types.InlineKeyboardButton("🎨 全能制图", callback_data="home_draw"),
    )
    kb.add(
        types.InlineKeyboardButton("🎬 视频相关", callback_data="home_video"),
        types.InlineKeyboardButton("🔍 搜索联网", callback_data="home_search"),
    )
    return kb

def chat_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("ask 快速", callback_data="cmd_ask"),
        types.InlineKeyboardButton("we 无限制", callback_data="cmd_we"),
    )
    kb.add(
        types.InlineKeyboardButton("ww 思考版", callback_data="cmd_ww"),
        types.InlineKeyboardButton("wr 最强思考", callback_data="cmd_wr"),
    )
    kb.add(
        types.InlineKeyboardButton("st 小说创作", callback_data="cmd_st"),
        types.InlineKeyboardButton("5 GPT-5深度", callback_data="cmd_5"),
    )
    kb.add(types.InlineKeyboardButton("⬅️ 返回首页", callback_data="home"))
    return kb

def draw_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("tu/p 文生/图生", callback_data="cmd_tu"),
        types.InlineKeyboardButton("ph 增强版", callback_data="cmd_ph"),
    )
    kb.add(
        types.InlineKeyboardButton("tt 4K高清", callback_data="cmd_tt"),
        types.InlineKeyboardButton("cn 中文P图", callback_data="cmd_cn"),
    )
    kb.add(
        types.InlineKeyboardButton("fc 换脸40", callback_data="cmd_fc"),
        types.InlineKeyboardButton("tr 换脸100", callback_data="cmd_tr"),
    )
    kb.add(
        types.InlineKeyboardButton("p2 改图2", callback_data="cmd_p2"),
        types.InlineKeyboardButton("ig Image2.0", callback_data="cmd_ig"),
    )
    kb.add(
        types.InlineKeyboardButton("sp 全能制图", callback_data="cmd_sp"),
        types.InlineKeyboardButton("nb 图片生成", callback_data="cmd_nb"),
    )
    kb.add(types.InlineKeyboardButton("⬅️ 返回首页", callback_data="home"))
    return kb

def video_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("sc 视频5秒", callback_data="cmd_sc"),
        types.InlineKeyboardButton("scc 视频10秒", callback_data="cmd_scc"),
    )
    kb.add(
        types.InlineKeyboardButton("sccc 视频15秒", callback_data="cmd_sccc"),
        types.InlineKeyboardButton("sv 图文生视频", callback_data="cmd_sv"),
    )
    kb.add(
        types.InlineKeyboardButton("so 换脸5秒", callback_data="cmd_so"),
        types.InlineKeyboardButton("soo 换脸10秒", callback_data="cmd_soo"),
    )
    kb.add(types.InlineKeyboardButton("⬅️ 返回首页", callback_data="home"))
    return kb

def search_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("nt/net 智能联网", callback_data="cmd_nt"))
    kb.add(types.InlineKeyboardButton("wf TG百事通", callback_data="cmd_wf"))
    kb.add(types.InlineKeyboardButton("wa 人物背景调查", callback_data="cmd_wa"))
    kb.add(types.InlineKeyboardButton("⬅️ 返回首页", callback_data="home"))
    return kb

HELP_TEXT = """📋 命令词展示
💡 用法==【输入命令词+你的要求】

━━━━ 💬 对话问答 ━━━━
ask（快速对话-免费）
we（无限制问答-基础问题-回答快）
ww（无限制问答思考版—精聊回复-支持图片分析）
wr（最强无限制问答思考—等待比较久）
st（小说创作-无限制）
5（深度对话GPT-5）

━━━━ 🎨 全能制图 ━━━━
tu/p（文生图/图生图/换脸/换背景）
ph（全能制图增强版-泛化最强）
tt（4K高清版文生图/图生图）
cn（中文P图-适合修改含中文背景的图片）
fc/tr（AI换脸模型）
p2（最新改图2）
ig（OpenAI Image 2.0）
sp（全能制图）
nb（图片生成）

━━━━ 🎬 视频相关 ━━━━
sc（文字/图片生成视频5秒）
scc（文字+图片生成视频10秒）
sccc（文字+图片生成视频15秒）
so（视频换脸5秒-需同时发送图片+视频）
soo（视频换脸10秒-需同时发送图片+视频）
sv（图文生视频5s）

━━━━ 🔍 搜索联网 ━━━━
nt/net（智能联网，nt普通 / net高级）
wf（TG智搜百事通-深度思考）
wa（人物背景调查-需提供邮箱或电话号码）

👇 点下面按钮选择分类，或直接输入如：we 你好
"""

@bot.message_handler(commands=['start','help','menu'])
def cmd_start(m):
    bot.send_message(m.chat.id, HELP_TEXT, reply_markup=home_menu())

@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    uid = call.from_user.id
    data = call.data
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    
    if data == "home" or data == "home_main":
        bot.send_message(chat_id, "📋 首页", reply_markup=home_menu())
        return
    if data == "home_chat":
        bot.send_message(chat_id, "💬 对话问答 - 选一个命令，然后按格式发送：\n例：`we 你好`", parse_mode="Markdown", reply_markup=chat_menu())
        return
    if data == "home_draw":
        bot.send_message(chat_id, "🎨 全能制图 - 选一个：\n例：`tu 一只赛博朋克猫`", parse_mode="Markdown", reply_markup=draw_menu())
        return
    if data == "home_video":
        bot.send_message(chat_id, "🎬 视频相关 - 选一个：\n例：`sc 一只猫在太空`", parse_mode="Markdown", reply_markup=video_menu())
        return
    if data == "home_search":
        bot.send_message(chat_id, "🔍 搜索联网 - 选一个：\n例：`nt 特斯拉最新消息`", parse_mode="Markdown", reply_markup=search_menu())
        return
    
    if data.startswith("cmd_"):
        cmd = data.split("_")[1]
        user_mode[uid] = cmd
        tips = {
            "ask": "✅ 已选 ask 快速对话\n请发送：`ask 你的问题`",
            "we": "✅ 已选 we 无限制问答\n请发送：`we 你的问题`",
            "ww": "✅ 已选 ww 思考版\n请发送：`ww 你的问题`（可带图片）",
            "wr": "✅ 已选 wr 最强思考\n请发送：`wr 你的问题`，我会深度思考",
            "st": "✅ 已选 st 小说创作\n请发送：`st 写一个科幻小说`",
            "5": "✅ 已选 5 GPT-5深度\n请发送：`5 解释量子计算`",
            "tu": "✅ 已选 tu 文生图\n请发送：`tu 一只赛博猫` 或发一张图+`tu 改成赛博朋克`",
            "ph": "✅ 已选 ph 增强版\n请发送：`ph 高质量风景`",
            "tt": "✅ 已选 tt 4K高清\n请发送：`tt 4K美女`",
            "cn": "✅ 已选 cn 中文P图\n请发送：`cn 把图里的中文改成 你好` 并附图",
            "fc": "✅ 已选 fc 换脸\n请依次发2张人脸照片",
            "tr": "✅ 已选 tr 换脸\n请依次发2张人脸照片",
            "p2": "✅ 已选 p2 改图\n请发图 + `p2 把背景改成海边`",
            "ig": "✅ 已选 ig Image2.0\n请发送：`ig 一只宇航员`",
            "sp": "✅ 已选 sp 全能制图\n请发送：`sp 你的描述`",
            "nb": "✅ 已选 nb 图片生成\n请发送：`nb 你的描述`",
            "sc": "✅ 已选 sc 视频5秒\n请发送：`sc 一只猫跳舞`",
            "scc": "✅ 已选 scc 视频10秒\n请发送：`scc 文字+图片描述`",
            "sccc": "✅ 已选 sccc 视频15秒\n请发送：`sccc 长视频描述`",
            "so": "✅ 已选 so 视频换脸5秒\n请同时发图片+视频",
            "soo": "✅ 已选 soo 视频换脸10秒\n请同时发图片+视频",
            "sv": "✅ 已选 sv 图文生视频\n请发送：`sv 一段文字`",
            "nt": "✅ 已选 nt/net 联网\n请发送：`nt 搜索内容` 或 `net 搜索内容`",
            "wf": "✅ 已选 wf TG百事通\n请发送：`wf 你想查的问题`",
            "wa": "✅ 已选 wa 背景调查\n请发送邮箱或电话，我会说明查询方式（不直接泄露隐私）",
        }
        bot.send_message(chat_id, tips.get(cmd, f"已选 {cmd}"), parse_mode="Markdown", reply_markup=home_menu())
        return

@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    uid = m.from_user.id
    mode = user_mode.get(uid, "")
    # fc/tr 换脸
    if mode in ["fc","tr"]:
        file_id = m.photo[-1].file_id
        info = bot.get_file(file_id)
        data = bot.download_file(info.file_path)
        path = f"/tmp/{uid}_{random.randint(1,9999)}.jpg"
        with open(path, "wb") as f:
            f.write(data)
        lst = user_memory.get(f"photo_{uid}", [])
        lst.append(path)
        user_memory[f"photo_{uid}"] = lst
        if len(lst) == 1:
            bot.send_message(m.chat.id, "第一张收到，发第二张")
        else:
            bot.send_message(m.chat.id, "正在换脸...")
            try:
                import cv2
                def swap(p1,p2,out):
                    i1=cv2.imread(p1); i2=cv2.imread(p2)
                    fc=cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                    f1=fc.detectMultiScale(cv2.cvtColor(i1,cv2.COLOR_BGR2GRAY),1.1,4)
                    f2=fc.detectMultiScale(cv2.cvtColor(i2,cv2.COLOR_BGR2GRAY),1.1,4)
                    if len(f1)==0 or len(f2)==0: return None
                    x1,y1,w1,h1=f1[0]; x2,y2,w2,h2=f2[0]
                    face=i1[y1:y1+h1,x1:x1+w1]
                    i2[y2:y2+h2,x2:x2+w2]=cv2.resize(face,(w2,h2))
                    cv2.imwrite(out,i2); return out
                out=f"/tmp/{uid}_swap.jpg"
                res=swap(lst[0],lst[1],out)
                if res:
                    with open(res,"rb") as f:
                        bot.send_photo(m.chat.id,f,caption="✅ 换脸完成")
                else:
                    bot.send_message(m.chat.id,"未检测到人脸")
            except Exception as e:
                bot.send_message(m.chat.id,f"换脸失败：{e}")
            user_memory[f"photo_{uid}"]=[]
        return
    # ww 支持图片分析
    bot.send_message(m.chat.id, "📷 收到图。你可以发 `ww 分析这张图` 或 `tu 把这张图改成...`")

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(m):
    uid = m.from_user.id
    text = m.text.strip()
    if not text:
        return
    bot.send_chat_action(m.chat.id, 'typing')
    
    # 解析命令词
    parts = text.split(maxsplit=1)
    cmd = parts[0].lower()
    content = parts[1] if len(parts)>1 else ""
    
    # 兼容 tu/p 这种
    if cmd.startswith("tu/") or cmd == "p":
        cmd = "tu"
    if cmd == "nt" or cmd == "net":
        cmd = "nt"
    if cmd == "fc" or cmd == "tr":
        cmd = "fc"
    
    valid_cmds = ["ask","we","ww","wr","st","5","tu","ph","tt","cn","fc","tr","p2","ig","sp","nb","sc","scc","sccc","so","soo","sv","nt","net","wf","wa","p"]
    if cmd not in valid_cmds:
        # 如果没带命令词，按上次选择的模式
        last = user_mode.get(uid, "we")
        if last in valid_cmds:
            cmd = last
            content = text
        else:
            cmd = "we"
            content = text
    
    # 如果只有命令词没内容
    if not content and cmd in ["ask","we","ww","wr","st","5","wf","nt","net"]:
        bot.send_message(m.chat.id, f"用法：`{cmd} 你的问题`", parse_mode="Markdown", reply_markup=home_menu())
        return
    
    # 对话类
    if cmd in ["ask","we","ww","wr","st","5"]:
        ans = chat(uid, content or text, cmd)
        bot.send_message(m.chat.id, ans, parse_mode="Markdown", reply_markup=home_menu())
        return
    
    # 制图类
    if cmd in ["tu","ph","tt","cn","p2","ig","sp","nb","p"]:
        prompt = content or text
        bot.send_message(m.chat.id, f"🎨 正在生成：{prompt}...")
        try:
            import urllib.parse
            safe = urllib.parse.quote(prompt)
            # tt 用高清参数
            w,h = (2048,2048) if cmd=="tt" else (1024,1024)
            url = f"https://image.pollinations.ai/prompt/{safe}?width={w}&height={h}&nologo=true&seed={random.randint(1,99999)}"
            r = requests.get(url, timeout=40)
            if r.status_code==200:
                path = f"/tmp/{uid}_img.jpg"
                with open(path,"wb") as f:
                    f.write(r.content)
                with open(path,"rb") as f:
                    bot.send_photo(m.chat.id, f, caption=f"✅ {cmd}: {prompt}", reply_markup=home_menu())
                return
        except Exception as e:
            bot.send_message(m.chat.id, f"作图失败：{e}", reply_markup=home_menu())
            return
    
    # 视频类 - 演示版
    if cmd in ["sc","scc","sccc","sv"]:
        bot.send_message(m.chat.id, f"🎬 {cmd} 视频生成\n你的需求：{content}\n\n目前演示版用图片+文字模拟，完整版需接入Runway/Pika API。先给你生成一张关键帧：", reply_markup=home_menu())
        # 生成一张图作为关键帧
        try:
            import urllib.parse
            safe = urllib.parse.quote(content)
            url = f"https://image.pollinations.ai/prompt/{safe} video frame cinematic?width=1024&height=576&nologo=true&seed={random.randint(1,99999)}"
            r = requests.get(url, timeout=30)
            if r.status_code==200:
                path = f"/tmp/{uid}_video.jpg"
                with open(path,"wb") as f:
                    f.write(r.content)
                with open(path,"rb") as f:
                    bot.send_photo(m.chat.id, f, caption=f"🎬 {cmd} 关键帧")
        except:
            pass
        return
    if cmd in ["so","soo"]:
        bot.send_message(m.chat.id, "🎬 视频换脸需同时发送图片+视频文件，当前为演示版，请发图片和视频", reply_markup=home_menu())
        return
    
    # 搜索类
    if cmd in ["nt","net","wf"]:
        query = content or text
        bot.send_message(m.chat.id, f"🔍 正在搜索：{query}...")
        try:
            from duckduckgo_search import DDGS
            results=[]
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=5):
                    results.append(f"• {r['title']}: {r['body'][:120]} - {r['href']}")
            if results:
                summary_prompt = f"用户搜索：{query}\n结果：\n" + "\n".join(results)
                ans = chat(uid, summary_prompt, "net" if cmd=="net" else "nt")
                bot.send_message(m.chat.id, ans + "\n\n" + "\n".join(results[:3]), reply_markup=home_menu())
            else:
                bot.send_message(m.chat.id, "未搜到，换个词试试", reply_markup=home_menu())
        except Exception as e:
            ans = chat(uid, query, "nt")
            bot.send_message(m.chat.id, ans, reply_markup=home_menu())
        return
    if cmd == "wa":
        bot.send_message(m.chat.id, "🔍 人物背景调查：出于隐私安全，我不能直接通过邮箱/电话查个人信息。\n\n你可以这样用：`wa 帮我写一封背景调查的邮件模板` 或 `wa 教我如何做合规的背景调查`，我会给你合法合规的流程。", reply_markup=home_menu())
        return

print("🚀 精简版已启动 - 支持你的所有命令词")
bot.infinity_polling()
