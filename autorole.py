import discord
from discord.ext import commands
import datetime

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # تأكد أن هذا هو آيدي الرتبة الصحيح
        self.AUTO_ROLE_ID = 1375197032192671847  # <--- ضع آيدي الرتبة هنا
        self.LOG_CHANNEL_ID = 1528789041934368900

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f"تم رصد دخول عضو جديد: {member.name}")
        
        # 1. التحقق من وجود الرتبة في السيرفر
        role = member.guild.get_role(self.AUTO_ROLE_ID)
        if not role:
            print(f"❌ خطأ: لم يتم العثور على الرتبة بالـ ID المحدد ({self.AUTO_ROLE_ID}). تأكد من نسخه بشكل صحيح.")
            return

        print(f"✅ تم العثور على الرتبة بنجاح: {role.name}")

        # 2. محاولة إعطاء الرتبة مع كشف نوع الخطأ بالتفصيل إن وجد
        try:
            await member.add_roles(role)
            print(f"🎉 تم إعطاء رتبة ({role.name}) للعضو: {member.name}")
            
            # إرسال السجل (Log)
            log_channel = member.guild.get_channel(self.LOG_CHANNEL_ID)
            if log_channel:
                embed = discord.Embed(
                    title="✨ سجل الأعضاء الجدد (Auto-Role)",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="👤 العضو الجديد", value=member.mention, inline=False)
                embed.add_field(name="🛡️ المسؤول (البوت)", value=self.bot.user.mention, inline=False)
                embed.add_field(name="⚖️ الإجراء المتخذ", value=f"منح رتبة: ({role.name})", inline=False)
                embed.add_field(name="📝 السبب", value="دخول العضو لأول مرة إلى السيرفر (Auto-Role)", inline=False)
                embed.set_footer(text=f"ID: {member.id}")
                
                await log_channel.send(embed=embed)
                
        except discord.Forbidden:
            print("❌ خطأ صلاحيات (Forbidden): البوت لا يمتلك صلاحية Manage Roles، أو أن رتبة البوت أدنى من الرتبة المراد إعطاؤها في قائمة رتب السيرفر!")
        except discord.HTTPException as e:
            print(f"❌ خطأ في الاتصال أو الطلب (HTTPException): {e}")
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {e}")

async def setup(bot):
    await bot.add_cog(AutoRole(bot))
