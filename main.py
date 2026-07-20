import discord
from discord.ext import commands
import datetime
import os

# إعدادات البوت الأساسية
intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------- إعدادات الروم المستهدف وروم السجلات -----------------
# 1. آيدي روم السجلات (Logs) الذي ستظهر فيه العقوبات
LOG_CHANNEL_ID = 1528789041934368900

# 2. آيدي الروم الوحيد الذي تريد حمايته ومنع إرسال الصور فيه (روم البداية)
# ضع آيدي الروم الخاص بالبداية هنا بدلاً من أصفار أو الرقم التجريبي
TARGET_CHANNEL_ID = 1528793300394574053  # <--- ضع آيدي روم البداية هنا

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح! بوت الحماية المخصص يعمل الآن باسم: {bot.user}")

# ----------------- نظام الحماية المخصص للروم المحدد فقط -----------------
@bot.event
async def on_message(message):
    # تجاهل رسائل البوتات
    if message.author.bot:
        return

    # الشرط الأساسي: هل الرسالة مرسلة في الروم المحدد بالبداية فقط؟
    # إذا كانت في روم آخر، البوت يتجاهلها تماماً ولا يفعل شيئاً
    if message.channel.id != TARGET_CHANNEL_ID:
        await bot.process_commands(message)
        return

    # من هنا فصاعداً، الكود سيشتغل فقط إذا كانت الرسالة داخل "روم البداية" المستهدف
    is_violation = False
    violation_reason = ""

    # إذا أرسل صورة في هذا الروم المخصص
    if message.attachments:
        is_violation = True
        violation_reason = "إرسال صورة مشبوهة / محاولة اختراق في روم البداية"

    # أو إذا كتب أي رابط أو كلمات مشبوهة
    content_lower = message.content.lower()
    if "http://" in content_lower or "https://" in content_lower:
        is_violation = True
        violation_reason = "إرسال رابط خارجي في روم البداية"

    # إذا حدثت مخالفة في هذا الروم
    if is_violation:
        try:
            # 1. حذف الرسالة أو الصورة فوراً
            await message.delete()
            
            # 2. معاقبة العضو بتايم أوت لمدة أسبوع (7 أيام)
            timeout_duration = datetime.timedelta(days=7)
            await message.author.timeout(timeout_duration, reason=violation_reason)

            # 3. إرسال السجل (Log) في روم السجلات المخصص
            log_channel = message.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="🚨 سجل الحماية (روم البداية)",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="👤 العضو المخترق", value=message.author.mention, inline=False)
                embed.add_field(name="🛡️ المسؤول (البوت)", value=bot.user.mention, inline=False)
                embed.add_field(name="⚖️ الإجراء المتخذ", value="تايم أوت لمدة أسبوع (7 أيام)", inline=False)
                embed.add_field(name="📝 السبب", value=violation_reason, inline=False)
                embed.set_footer(text=f"ID: {message.author.id}")
                
                await log_channel.send(embed=embed)

            # 4. تنبيه مؤقت في نفس روم البداية ثم حذفه بعد 10 ثواني
            warning_msg = await message.channel.send(f"🚨 تنبيه {message.author.mention}: ممنوع إرسال الصور أو الروابط هنا! تم إعطاؤك تايم أوت أسبوع.")
            await warning_msg.delete(delay=10)
            
            print(f"تم التصدي لمحاولة في روم البداية من العضو: {message.author.name}")
        except Exception as e:
            print(f"خطأ أثناء تنفيذ العقوبة في روم البداية: {e}")

    await bot.process_commands(message)

# تشغيل البوت عبر بيئة العمل الآمنة في Railway أو التوكن المباشر
TOKEN = os.getenv('TOKEN') or 'ضع_التوكين_هنا_إذا_لم_تستخدم_متغيرات_البيئة'
bot.run(TOKEN)
