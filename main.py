import discord
from discord.ext import commands
import datetime
import os

# 1. تفعيل الصلاحيات الشاملة بما فيها الأعضاء بشكل صريح
intents = discord.Intents.all()  # استخدام .all() يحل أي مشكلة نقص في الصلاحيات فوراً
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------- الإعدادات والمتغيرات -----------------
LOG_CHANNEL_ID = 1528789041934368900       # آيدي روم السجلات
TARGET_CHANNEL_ID = 1528793300394574053      # <--- ضع آيدي روم البداية هنا للحماية
AUTO_ROLE_ID = 1375197032192671847          # آيدي رتبة Member الخاصة بالأعضاء الجدد

@bot.event
async def on_ready():
    print(f"========================================")
    print(f"تم تسجيل الدخول بنجاح!")
    print(f"اسم البوت: {bot.user.name}")
    print(f"البوت متصل وجاهز لرصد الأعضاء والحماية!")
    print(f"========================================")

# ----------------- نظام الأوتو رول عند دخول العضو -----------------
@bot.event
async def on_member_join(member):
    print(f">>> تم رصد دخول عضو جديد للسيرفر: {member.name} (ID: {member.id})")
    try:
        # جلب الرتبة باستخدام الـ ID
        role = member.guild.get_role(AUTO_ROLE_ID)
        if role:
            # إعطاء الرتبة للعضو
            await member.add_roles(role)
            print(f"🎉 نجاح: تم إعطاء رتبة ({role.name}) للعضو: {member.name}")
            
            # إرسال سجل (Log) في روم السجلات
            log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="✨ سجل الأعضاء الجدد (Auto-Role)",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="👤 :العضو الجديد", value=member.mention, inline=False)
                embed.add_field(name="🛡️ :المسؤول (البوت)", value=bot.user.mention, inline=False)
                embed.add_field(name="⚖️ :الإجراء المتخذ", value=f"منح رتبة: ({role.name})", inline=False)
                embed.add_field(name="📝 :السبب", value="دخول العضو لأول مرة إلى السيرفر (Auto-Role)", inline=False)
                embed.set_footer(text=f"ID: {member.id}")
                
                await log_channel.send(embed=embed)
        else:
            print(f"❌ خطأ: لم يتم العثور على الرتبة بالـ ID المحدد ({AUTO_ROLE_ID}). تأكد من رقم الرتبة.")
    except Exception as e:
        print(f"❌ خطأ أثناء إعطاء الرتبة أو إرسال اللوج: {e}")

# ----------------- نظام الحماية في روم البداية فقط -----------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # فحص هل الرسالة في روم البداية المستهدف فقط؟
    if message.channel.id != TARGET_CHANNEL_ID:
        await bot.process_commands(message)
        return

    is_violation = False
    violation_reason = ""

    if message.attachments:
        is_violation = True
        violation_reason = "إرسال صورة مشبوهة او غير مرغوب فيها / حساب مخترق"

    content_lower = message.content.lower()
    if "http://" in content_lower or "https://" in content_lower:
        is_violation = True
        violation_reason = "إرسال رابط خارجي في روم البداية"

    if is_violation:
        try:
            await message.delete()
            timeout_duration = datetime.timedelta(days=7)
            await message.author.timeout(timeout_duration, reason=violation_reason)

            log_channel = message.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="🚨 سجل الحماية (من حسابات الاعضاء المخترقة)",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="👤 :العضو المخترق", value=message.author.mention, inline=False)
                embed.add_field(name="🛡️ :المسؤول (البوت)", value=bot.user.mention, inline=False)
                embed.add_field(name="⚖️ :الإجراء المتخذ", value="تايم أوت لمدة أسبوع (7 أيام)", inline=False)
                embed.add_field(name="📝 :السبب", value=violation_reason, inline=False)
                embed.set_footer(text=f"ID: {message.author.id}")
                
                await log_channel.send(embed=embed)

            warning_msg = await message.channel.send(f"🚨 تنبيه {message.author.mention}: ممنوع إرسال الصور أو الروابط هنا! تم إعطاؤك تايم أوت أسبوع.")
            await warning_msg.delete(delay=11)
        except Exception as e:
            print(f"خطأ أثناء الحماية: {e}")

    await bot.process_commands(message)

# تشغيل البوت
TOKEN = os.getenv('TOKEN') or 'ضع_التوكين_هنا_إذا_لم_تستخدم_متغيرات_البيئة'
bot.run(TOKEN)
