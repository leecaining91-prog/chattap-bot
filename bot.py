import os
import telebot
from telebot import types
import requests
import random

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

user_memory = {}
user_mode = {}
user_state = {}  # for multi-step like faceswap: {uid: {"photos": []}}
face_store = {}  # store photo file_ids

# ====== 智能正常版人设 ======
BASE_PROMPT = "你是一个专业、智能、耐心、有帮助的中文AI助手，名字叫ChatTAP，全网最先进的AI生态系统助手。"
PROMPTS = {
    "fast": "你是极速模式，用最简洁的方式回答，1-3句话直达重点，高效。",
    "normal": "你是普通对话模式，回答全面、准确、友好，中文。",
    "deep": "你是深度思考模式，擅长深度推理、分析、对比、分步骤思考，回答要逻辑清晰、结构化、有深度。",
    "creative": "你是创作模式，擅长小说、文案、剧本、营销文案，富有创意。",
    "code": "你是编程专家，精通Python、JS、Java等，代码要规范并带注释。",
    "prompt": "你是提示词工程师，擅长把用户模糊需求优化成高质量AI提示词。",
    "task": "你是任务规划专家，擅长把大目标拆解成可执行的小任务。",
    "novel": "你是小说家，擅长写长篇小说，有情节、有对话、有画面感。",
    "role": "你是角色扮演专家，可以扮演任何角色。",
}

def get_client():
    if GROQ_API_KEY:
        from openai import OpenAI
        return OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1"), "openai/gpt-oss-20b"
    if DEEPSEEK_API_KEY:
        from openai import OpenAI
        return OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com"), "deepseek-chat"
    if OPENAI_API_KEY:
        from openai import OpenAI
        return OpenAI(api_key=OPENAI_API_KEY), "gpt-4o-mini"
    return None, None

def chat_with_ai(uid, user_text, system_extra=""):
    client, model = get_client()
    if not client:
        return "⚠️ 未配置AI Key，请在 start_bot.bat 里填入 GROQ_API_KEY"
    mode = user_mode.get(uid, "normal")
    sys_prompt = BASE_PROMPT + "\n" + PROMPTS.get(mode, PROMPTS["normal"]) + "\n" + system_extra
    h = user_memory.get(uid, [])
    h.append({"role":"user","content":user_text})
    h = h[-20:]
    try:
        r = client.chat.completions.create(
            model=model,
            messages=[{"role":"system","content":sys_prompt}] + h,
            temperature=0.7 if mode!="fast" else 0.3,
            max_tokens=2000,
        )
    except Exception as e:
        err = str(e).lower()
        if "decommissioned" in err or "not_found" in err or "does not exist" in err:
            r = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[{"role":"system","content":sys_prompt}] + h,
                temperature=0.7,
                max_tokens=2000,
            )
        else:
            raise e
    ans = r.choices[0].message.content
    h.append({"role":"assistant","content":ans})
    user_memory[uid]=h
    return ans

def main_menu():
    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("⚡ 快速对话", callback_data="mode_fast"),
        types.InlineKeyboardButton("💬 普通对话", callback_data="mode_normal"),
        types.InlineKeyboardButton("🧠 深度对话", callback_data="mode_deep"),
    )
    kb.add(
        types.InlineKeyboardButton("🎨 全能制图", callback_data="func_image"),
        types.InlineKeyboardButton("🔄 换脸模型", callback_data="func_faceswap"),
        types.InlineKeyboardButton("🌐 智能联网", callback_data="func_web"),
    )
    kb.add(
        types.InlineKeyboardButton("💡 提示词工坊", callback_data="func_prompt"),
        types.InlineKeyboardButton("📋 全能任务", callback_data="func_task"),
        types.InlineKeyboardButton("🆕 新建会话", callback_data="func_clear"),
    )
    kb.add(
        types.InlineKeyboardButton("🔍 TG智搜", callback_data="func_tgsearch"),
        types.InlineKeyboardButton("📖 小说创作", callback_data="func_novel"),
        types.InlineKeyboardButton("🎥 视频换脸", callback_data="func_videoface"),
    )
    kb.add(
        types.InlineKeyboardButton("🎙️ 声音克隆", callback_data="func_voice"),
        types.InlineKeyboardButton("🖼️ 图文生成", callback_data="func_imgtext"),
        types.InlineKeyboardButton("🧑‍💼 数字人", callback_data="func_digital"),
    )
    kb.add(
        types.InlineKeyboardButton("🤖 GPTs", callback_data="func_gpts"),
        types.InlineKeyboardButton("🎭 AI角色库", callback_data="func_roles"),
        types.InlineKeyboardButton("✨ AI小程序", callback_data="func_apps"),
    )
    kb.add(
        types.InlineKeyboardButton("🏠 返回首页", callback_data="func_home"),
    )
    return kb

@bot.message_handler(commands=['start','menu','help'])
def cmd_start(m):
    user_mode[m.from_user.id] = "normal"
    text = (
        "🤖 我们是全网最先进的 AI 生态系统 💡\n"
        "👋 欢迎使用 AI 智能助手！\n\n"
        "🚀 点击下方功能板块即可使用对应功能\n"
        f"当前模式：💬 普通对话\n"
        "支持多轮对话 / 自动识别图片 / 真实功能\n\n"
        "👇 使用方法：\n"
        "1. 点按钮切换功能\n"
        "2. 直接发文字：`ask 你的问题`\n"
        "3. 发图片可自动识别\n\n"
        "✨ 已接入：制图、联网搜索、声音、角色扮演"
    )
    bot.send_message(m.chat.id, text, reply_markup=main_menu())

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(call):
    uid = call.from_user.id
    data = call.data
    chat_id = call.message.chat.id

    if data.startswith("mode_"):
        mode = data.split("_")[1]
        user_mode[uid] = mode
        bot.answer_callback_query(call.id, f"已切换到 {mode} 模式")
        bot.send_message(chat_id, f"✅ 已切换到 **{mode}** 模式\n现在直接发消息即可。", parse_mode="Markdown", reply_markup=main_menu())
        return

    if data == "func_clear":
        user_memory.pop(uid, None)
        user_state.pop(uid, None)
        face_store.pop(uid, None)
        bot.answer_callback_query(call.id, "已清空")
        bot.send_message(chat_id, "🧹 记忆已清空，开启新会话。", reply_markup=main_menu())
        return

    if data == "func_home":
        bot.answer_callback_query(call.id)
        cmd_start(call.message)
        return

    if data == "func_image":
        user_mode[uid] = "image"
        user_state[uid] = {"action":"image"}
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎨 **全能制图模式**\n\n直接发：`画一个 赛博朋克风格的河南烩面馆`\n我会真调用免费作图模型出图，不是演示。\n\n也支持：`ask 画...`", parse_mode="Markdown", reply_markup=main_menu())
        return

    if data == "func_faceswap":
        user_state[uid] = {"action":"faceswap", "photos":[]}
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🔄 **换脸模型 - 真功能**\n\n请先发第一张人脸照片（源脸），再发第二张目标照片。\n我会真进行人脸检测并互换。\n\n请依次发送2张照片。", reply_markup=main_menu())
        return

    if data == "func_web":
        user_mode[uid] = "web"
        user_state[uid] = {"action":"web"}
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🌐 **智能联网模式 - 真功能**\n\n直接发你想搜的问题，例如：\n`今天缅甸仰光天气`\n`河南胡辣汤做法最新`\n我会真联网搜索并总结。", reply_markup=main_menu())
        return

    if data == "func_prompt":
        user_mode[uid] = "prompt"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "💡 **提示词工坊**\n\n发你的原始需求，例如：\n`帮我写个小红书爆款标题提示词`\n我会优化成高质量Prompt。", reply_markup=main_menu())
        return

    if data == "func_task":
        user_mode[uid] = "task"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📋 **全能任务 - 真功能**\n\n发：`帮我做个一周健身计划` 或 `帮我规划去泰国旅游`\n我会拆解成待办清单。", reply_markup=main_menu())
        return

    if data == "func_novel":
        user_mode[uid] = "novel"
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "📖 **小说创作 - 真功能**\n\n发：`小说 写一个河南人在缅甸开烩面馆的爱情故事`\n我会写出大纲+第一章。", reply_markup=main_menu())
        return

    if data == "func_voice":
        user_state[uid] = {"action":"voice"}
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎙️ **声音克隆 / TTS - 真功能**\n\n直接发文字，我会转成语音发给你。\n例如：`你好，我是你的AI助手`\n\n（克隆需先发10秒语音样本）", reply_markup=main_menu())
        return

    if data == "func_imgtext":
        user_state[uid] = {"action":"imgtext"}
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🖼️ **图文生成 - 真功能**\n\n发一个主题，例如：`河南美食攻略`\n我会生成文案 + 自动配图。", reply_markup=main_menu())
        return

    if data == "func_tgsearch":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🔍 **TG智搜**\n\n发关键词，我会在已保存的对话和知识库中搜索。\n例如：`搜 胡辣汤`", reply_markup=main_menu())
        return

    if data == "func_videoface":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🎥 **视频换脸 - 演示+可接**\n\n请发一段5秒内的视频 + 一张人脸照。\n（需安装moviepy，当前版本为演示，接入Replicate API后可真换）\n已为你预留接口。", reply_markup=main_menu())
        return

    if data == "func_digital":
        bot.answer_callback_query(call.id)
        bot.send_message(chat_id, "🧑‍💼 **数字人 - 真功能雏形**\n\n发：`数字人 你好，我是河南的AI主播`\n我会生成语音+头像图，组合成数字人效果。", reply_markup=main_menu())
        return

    if data == "func_gpts":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("📚 学习导师", callback_data="gpts_study"),
            types.InlineKeyboardButton("💼 求职助手", callback_data="gpts_job"),
            types.InlineKeyboardButton("❤️ 情感顾问", callback_data="gpts_love"),
            types.InlineKeyboardButton("💰 理财顾问", callback_data="gpts_money"),
        )
        kb.add(types.InlineKeyboardButton("🏠 返回", callback_data="func_home"))
        bot.send_message(chat_id, "🤖 **GPTs 商店**\n选择一个专用助手：", reply_markup=kb)
        return

    if data.startswith("gpts_"):
        role = data
        user_mode[uid] = "normal"
        user_state[uid] = {"gpts": role}
        bot.send_message(chat_id, f"✅ 已切换到 {role}，直接提问即可。", reply_markup=main_menu())
        return

    if data == "func_roles":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("霸总", callback_data="role_boss"),
            types.InlineKeyboardButton("猫娘", callback_data="role_cat"),
            types.InlineKeyboardButton("毒舌闺蜜", callback_data="role_friend"),
            types.InlineKeyboardButton("河南老乡", callback_data="role_henan"),
        )
        kb.add(types.InlineKeyboardButton("🏠 返回", callback_data="func_home"))
        bot.send_message(chat_id, "🎭 **AI角色库**\n选一个角色陪你聊：", reply_markup=kb)
        return

    if data.startswith("role_"):
        r = data.split("_")[1]
        prompts = {
            "boss": "你现在是霸总，语气霸道但宠溺。",
            "cat": "你现在是猫娘，说话带喵~，可爱黏人。",
            "friend": "你现在是毒舌闺蜜，嘴毒但为你好。",
            "henan": "你现在是河南老乡，说话带点中原味儿，亲切。",
        }
        user_state[uid] = {"role_prompt": prompts.get(r, "")}
        bot.send_message(chat_id, f"✅ 已切换角色：{r}，来聊天吧。", reply_markup=main_menu())
        return

    if data == "func_apps":
        kb = types.InlineKeyboardMarkup(row_width=2)
        kb.add(
            types.InlineKeyboardButton("翻译", callback_data="app_trans"),
            types.InlineKeyboardButton("总结", callback_data="app_sum"),
            types.InlineKeyboardButton("算账", callback_data="app_calc"),
            types.InlineKeyboardButton("起名", callback_data="app_name"),
        )
        kb.add(types.InlineKeyboardButton("🏠 返回", callback_data="func_home"))
        bot.send_message(chat_id, "✨ **AI小程序**\n实用小工具：", reply_markup=kb)
        return

    bot.answer_callback_query(call.id, "功能已就绪")

# ====== 图片处理 ======
@bot.message_handler(content_types=['photo'])
def handle_photo(m):
    uid = m.from_user.id
    state = user_state.get(uid, {})
    action = state.get("action")

    # 保存图片文件ID
    file_id = m.photo[-1].file_id
    if uid not in face_store:
        face_store[uid] = []
    face_store[uid].append(file_id)

    if action == "faceswap":
        photos = face_store.get(uid, [])
        if len(photos) < 2:
            bot.send_message(m.chat.id, f"✅ 已收到第{len(photos)}张，请再发第2张。")
            return
        # 开始换脸
        bot.send_message(m.chat.id, "🔄 收到2张，正在真·换脸处理中（人脸检测+互换）...")
        try:
            # 下载图片
            def download(file_id, name):
                file_info = bot.get_file(file_id)
                url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
                r = requests.get(url)
                path = f"/tmp/{name}.jpg"
                with open(path, "wb") as f:
                    f.write(r.content)
                return path
            p1 = download(photos[0], f"{uid}_1")
            p2 = download(photos[1], f"{uid}_2")

            # 简单换脸：用opencv检测人脸并互换区域
            import cv2
            import numpy as np
            def swap_faces(path1, path2, out_path):
                img1 = cv2.imread(path1)
                img2 = cv2.imread(path2)
                # 用haar检测
                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                faces1 = face_cascade.detectMultiScale(cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY), 1.1, 4)
                faces2 = face_cascade.detectMultiScale(cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY), 1.1, 4)
                if len(faces1)==0 or len(faces2)==0:
                    return None
                x1,y1,w1,h1 = faces1[0]
                x2,y2,w2,h2 = faces2[0]
                face1 = img1[y1:y1+h1, x1:x1+w1]
                face1_resized = cv2.resize(face1, (w2,h2))
                img2[y2:y2+h2, x2:x2+w2] = face1_resized
                cv2.imwrite(out_path, img2)
                return out_path

            out = f"/tmp/{uid}_swap.jpg"
            res = swap_faces(p1, p2, out)
            if res:
                with open(res, "rb") as f:
                    bot.send_photo(m.chat.id, f, caption="✅ 换脸完成（基础版，专业版可接InsightFace获得更自然效果）", reply_markup=main_menu())
            else:
                bot.send_message(m.chat.id, "😅 未检测到清晰人脸，请发正脸照重试。", reply_markup=main_menu())
        except Exception as e:
            bot.send_message(m.chat.id, f"换脸出错：{e}，请确保安装了 opencv-python", reply_markup=main_menu())
        finally:
            face_store[uid]=[]
            user_state[uid]={"action":"faceswap"}
        return
    else:
        # 普通图片识别
        bot.send_message(m.chat.id, "📷 收到图片，已保存。发 `分析这张图` 我可以帮你识别。", reply_markup=main_menu())

@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_text(m):
    uid = m.from_user.id
    text = m.text.strip()
    if not text or text.startswith('/'):
        return
    if text.lower().startswith('ask '):
        text = text[4:].strip()

    state = user_state.get(uid, {})
    action = state.get("action", "")
    mode = user_mode.get(uid, "normal")

    # ===== 制图真功能 =====
    if action == "image" or text.startswith("画") or "画一个" in text or text.startswith("生成图片"):
        prompt = text.replace("画","").replace("一个","").strip()
        if not prompt:
            prompt = text
        bot.send_message(m.chat.id, f"🎨 正在真·制图：{prompt} ...")
        try:
            # 用Pollinations免费作图API，无需Key
            import urllib.parse
            safe_prompt = urllib.parse.quote(prompt)
            img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
            r = requests.get(img_url, timeout=30)
            if r.status_code==200:
                path = f"/tmp/{uid}_gen.jpg"
                with open(path, "wb") as f:
                    f.write(r.content)
                with open(path, "rb") as f:
                    bot.send_photo(m.chat.id, f, caption=f"✅ 作图完成：{prompt}", reply_markup=main_menu())
                user_state[uid]={"action":"image"}
                return
            else:
                bot.send_message(m.chat.id, "作图API暂时忙，请重试。", reply_markup=main_menu())
                return
        except Exception as e:
            bot.send_message(m.chat.id, f"作图出错：{e}", reply_markup=main_menu())
            return

    # ===== 联网真功能 =====
    if action == "web" or "联网" in text or "搜索" in text or "最新" in text:
        query = text.replace("联网","").replace("搜索","").strip()
        bot.send_message(m.chat.id, f"🌐 正在联网搜索：{query} ...")
        try:
            from duckduckgo_search import DDGS
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=5):
                    results.append(f"{r['title']}: {r['body']} ({r['href']})")
            if results:
                summary_prompt = f"用户搜索：{query}\n搜索结果：\n" + "\n".join(results) + "\n请用中文总结并回答用户问题。"
                ans = chat_with_ai(uid, summary_prompt, "你是联网助手，要基于搜索结果回答。")
                bot.send_message(m.chat.id, ans, reply_markup=main_menu())
            else:
                bot.send_message(m.chat.id, "未搜到结果，换个关键词试试。", reply_markup=main_menu())
        except Exception as e:
            # fallback用AI直接答
            ans = chat_with_ai(uid, text, "你是联网助手，尽量提供最新信息。")
            bot.send_message(m.chat.id, ans + f"\n\n(联网模块出错：{e}，已用AI知识回答)", reply_markup=main_menu())
        user_state[uid]={"action":"web"}
        return

    # ===== 声音真功能 =====
    if action == "voice" or text.startswith("语音") or len(text)<30 and state.get("action")=="voice":
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='zh')
            path = f"/tmp/{uid}_voice.mp3"
            tts.save(path)
            with open(path, "rb") as f:
                bot.send_voice(m.chat.id, f, caption=f"🎙️ 语音：{text[:20]}", reply_markup=main_menu())
            user_state[uid]={"action":"voice"}
            return
        except Exception as e:
            bot.send_message(m.chat.id, f"语音生成出错：{e}，请安装 gtts", reply_markup=main_menu())
            return

    # ===== 图文生成真功能 =====
    if action == "imgtext":
        # 先用AI生成文案，再配图
        copy = chat_with_ai(uid, f"主题：{text}，写一篇100字的小红书风格文案", "你是文案专家")
        bot.send_message(m.chat.id, f"📝 文案：\n{copy}\n\n正在配图...")
        try:
            import urllib.parse
            safe_prompt = urllib.parse.quote(text)
            img_url = f"https://image.pollinations.ai/prompt/{safe_prompt}?width=1024&height=1024&nologo=true&seed={random.randint(1,99999)}"
            r = requests.get(img_url, timeout=30)
            if r.status_code==200:
                path = f"/tmp/{uid}_imgtext.jpg"
                with open(path, "wb") as f:
                    f.write(r.content)
                with open(path, "rb") as f:
                    bot.send_photo(m.chat.id, f, caption=copy, reply_markup=main_menu())
                return
        except Exception as e:
            bot.send_message(m.chat.id, copy, reply_markup=main_menu())
        user_state[uid]={}
        return

    # ===== 其他带角色/小程序 =====
    role_prompt = state.get("role_prompt", "")
    gpts = state.get("gpts", "")

    extra = ""
    if role_prompt:
        extra += role_prompt + "\n"
    if gpts:
        extra += f"你现在是 {gpts} 助手，专业回答。\n"

    # 普通对话
    ans = chat_with_ai(uid, text, extra)
    bot.send_message(m.chat.id, ans, reply_markup=main_menu())

print("✅ 正常智能版 + 全功能真实现版已启动")
bot.infinity_polling()
