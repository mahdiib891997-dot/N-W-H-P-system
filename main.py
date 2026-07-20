import discord
from discord.ext import commands
import datetime
import os

# إعدادات البوت الأساسية
intents = discord.Intents.default()
intents.members = True # ضروري للتفاعل مع أعضاء السيرفر
intents.message_content = True # ضروري جداً لقراءة محتوى الرسائل
bot = commands.Bot(command_prefix="!", intents=intents)

# إعدادات روم السجلات (Logs)
LOG_CHANNEL_ID = 1528789041934368900

# كلمات مفتاحية احتياطية (لو كتب نص مع الصورة)
SCAM_KEYWORDS = [
    "nitro", "free nitro", "steamgift", "steam-nitro", 
    "airdrop", "crypto", "usdt", "giveaway", "tasowin", 
    "robux", "discord.gift", "discorb.com", "steampay"
]

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح! بوت حماية الصور يعمل الآن باسم: {bot.user}")

# ----------------- نظام الحماية المشدد ضد الصور والروابط الخبيثة -----------------
@bot.event
async def on_message(message):
    # تجاهل رسائل البوتات
    if message.author.bot:
        return

    content_lower = message.content.lower()
    is_scam = False
    violation_reason = ""

    # 1. فحص إذا كانت الرسالة تحتوي على "صور مرفقة" (Attachments) -> هذا هو الأهم بناءً على طلبك
    if message.attachments:
        is_scam = True
        violation_reason = "إرسال صورة مشبوهة / صورة اختراق محتملة"

    # 2. فحص الكلمات المفتاحية النصية في حال وجدت
    for word in SCAM_KEYWORDS:
        if word in content_lower:
            is_scam = True
            violation_reason = f"إرسال رابط أو كلمات مشبوهة (تحتوي على: {word})"
            break

    # إذا تأكد البوت أن هناك صورة أو رسالة مخالفة
    if is_scam:
        try:
            # أولاً: حذف الصورة أو الرسالة فوراً
            await message.delete()
            
            # ثانياً: معاقبة العضو المخترق بإعطائه "تايم أوت" (Timeout) لمدة أسبوع كامل (7 أيام)
            timeout_duration = datetime.timedelta(days=7)
            await message.author.timeout(timeout_duration, reason=violation_reason)

            # ثالثاً: إرسال تفاصيل العقوبة في روم السجلات (Log Channel) بالـ ID الصحيح
            log_channel = message.guild.get_channel(LOG_CHANNEL_ID)
            
            # إذا لم يتم العثور عليه بالـ ID، يبحث عنه بالاسم احتياطياً
            if not log_channel:1528789041934368900
            for channel in message.guild.text_channels:
                    if channel.name in ["bot-logs", "سجلات-البوت", "log", "logs"]:
                        log_channel = channel
                        break

            # إذا وُجد روم السجلات، يتم إرسال السجل (Embed)
            if log_channel:
                embed = discord.Embed(
                    title="🚨 سجل عقوبات حماية السيرفر (صور/هكر)",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="👤 العضو المخترق", value=message.author.mention, inline=False)
                embed.add_field(name="🛡️ المسؤول (البوت)", value=bot.user.mention, inline=False)
                embed.add_field(name="⚖️ الإجراء المتخذ", value="تايم أوت لمدة أسبوع (7 أيام)", inline=False)
                embed.add_field(name="📝 السبب", value=violation_reason, inline=False)
                embed.set_footer(text=f"ID: {message.author.id}")
                
                await log_channel.send(embed=embed)

            # رابعاً: إرسال تنبيه مؤقت في الشات العام ثم حذفه بعد 10 ثواني
            warning_msg = await message.channel.send(f"🚨 **نظام الحماية:** تم رصد صورة/رسالة مشبوهة من العضو {message.author.mention}، وتم حذفها وإعطاؤه تايم أوت أسبوع.")
            await warning_msg.delete(delay=10)
            
            print(f"تم حذف صورة/رسالة مخترق بنجاح من العضو: {message.author.name} والسبب: {violation_reason}")
        except Exception as e:
            print(f"خطأ أثناء معاقبة المخترق وإرسال السجل: {e}")

    # السماح بالأوامر الأخرى
    await bot.process_commands(message)

# تشغيل البوت عبر بيئة العمل الآمنة في Railway أو التوكن المباشر
TOKEN = os.getenv('TOKEN') or 'ضع_التوكين_هنا_إذا_لم_تستخدم_متغيرات_البيئة'
bot.run(TOKEN)
