import discord
from discord.ext import commands
import datetime
import os

# إعدادات البوت الأساسية
intents = discord.Intents.default()
intents.members = True # ضروري للتفاعل مع أعضاء السيرفر
intents.message_content = True # ضروري جداً لقراءة محتوى الرسائل وحظر الروابط والهكر
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------- إعدادات روم السجلات (Logs) -----------------
# ضع الـ ID الخاص بروم السجلات الذي خصصته للعقوبات هنا (مثلاً: 123456789123456789)
# إذا تركته 0، سيحاول البوت البحث عن روم اسمه "bot-logs" أو "سجلات-البوت" تلقائياً
LOG_CHANNEL_ID = 1528789041934368900

# قائمة الكلمات والروابط الشهيرة المرتبطة بالاختراق والمسابقات الوهمية (مثل الصور المزيفة)
SCAM_KEYWORDS = [
    "nitro", "free nitro", "steamgift", "steam-nitro", 
    "airdrop", "crypto", "usdt", "giveaway", "tasowin", 
    "robux", "discord.gift", "discorb.com", "steampay"
]

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح! بوت الحماية يعمل الآن باسم: {bot.user}")

# ----------------- نظام الحماية الشامل ضد الهكر والروابط -----------------
@bot.event
async def on_message(message):
    # تجاهل رسائل البوتات
    if message.author.bot:
        return

    content_lower = message.content.lower()
    is_scam = False
    violation_reason = ""

    # 1. فحص نص الرسالة بحثاً عن كلمات أو روابط سرقة الحسابات الشائعة
    for word in SCAM_KEYWORDS:
        if word in content_lower:
            is_scam = True
            violation_reason = f"إرسال رابط أو كلمات مشبوهة (تحتوي على: {word})"
            break

    # 2. فحص الروابط الخارجية (إذا أردت حظر أي رابط غريب يحتوي على http أو https)
    if "http://" in content_lower or "https://" in content_lower:
        # إذا أردت تفعيل حظر كل الروابط الخارجية، أزل علامة الـ # عن السطر التالي:
        # is_scam = True
        # violation_reason = "إرسال رابط خارجي مشبوه"
        pass

    # 3. فحص إذا كانت الرسالة تحتوي على صور مرفقة مع كلمات مفتاحية مشبوهة
    if message.attachments and is_scam:
        violation_reason = "إرسال صورة ومحتوى اختراق مسروق"

    # إذا تأكد البوت أن الرسالة تخص هكر أو عملية اختراق
    if is_scam:
        try:
            # أولاً: حذف الرسالة فوراً قبل أن يراها أو يضغط عليها أحد
            await message.delete()
            
            # ثانياً: معاقبة العضو المخترق بإعطائه "تايم أوت" (Timeout) لمدة أسبوع كامل (7 أيام)
            timeout_duration = datetime.timedelta(days=7)
            await message.author.timeout(timeout_duration, reason=violation_reason)

            # ثالثاً: إرسال تفاصيل العقوبة في روم السجلات (Log Channel)
            log_channel = None
            
            # محاولة العثور على روم السجلات بالـ ID أو بالاسم
            if LOG_CHANNEL_ID != 1528789041934368900:
                log_channel = message.guild.get_channel(LOG_CHANNEL_ID)
            else:
                for channel in message.guild.text_channels:
                    if channel.name in ["bot-logs", "سجلات-البوت", "log", "logs"]:
                        log_channel = channel
                        break

            # إذا وُجد روم السجلات، يتم إرسال رسالة منسقة ومرتبة
            if log_channel:
                embed = discord.Embed(
                    title="🚨 سجل عقوبات حماية السيرفر",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="👤 العضو المخترق", value=message.author.mention, inline=False)
                embed.add_field(name="🛡️ المسؤول (البوت)", value=bot.user.mention, inline=False)
                embed.add_field(name="⚖️ الإجراء المتخذ", value="تايم أوت لمدة أسبوع (7 أيام)", inline=False)
                embed.add_field(name="📝 السبب", value=violation_reason, inline=False)
                embed.set_footer(text=f"ID: {message.author.id}")
                
                await log_channel.send(embed=embed)

            # رابعاً: إرسال تنبيه مؤقت في الشات العام ثم حذفه بعد 10 ثواني ليبقى المكان نظيفاً
            warning_msg = await message.channel.send(f"🚨 **نظام الحماية:** تم رصد محاولة اختراق من العضو {message.author.mention}، وتم اتخاذ الإجراء بحقه ونشر التفاصيل في سجلات البوت.")
            await warning_msg.delete(delay=10)
            
            print(f"تم التصدي لمحاولة اختراق بنجاح من العضو: {message.author.name} والسبب: {violation_reason}")
        except Exception as e:
            print(f"خطأ أثناء معاقبة المخترق وإرسال السجل: {e}")

    # السماح بالأوامر الأخرى
    await bot.process_commands(message)

# تشغيل البوت عبر بيئة العمل الآمنة في Railway أو التوكن المباشر
TOKEN = os.getenv('TOKEN') or 'ضع_التوكين_هنا_إذا_لم_تستخدم_متغيرات_البيئة'
bot.run(TOKEN)