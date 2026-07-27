import discord
from discord.ext import commands
import datetime

class AutoRole(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 1. ضع آيدي الرتبة الخاصة بالأعضاء الجدد هنا
        self.AUTO_ROLE_ID = 1375197032192671847  # <--- ضع آيدي الرتبة هنا
        
        # 2. آيدي روم السجلات (Logs) الذي سيتم إرسال السجل فيه
        self.LOG_CHANNEL_ID = 1528789041934368900

    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            role = member.guild.get_role(self.AUTO_ROLE_ID)
            if role:
                # إعطاء الرتبة للعضو
                await member.add_roles(role)
                
                # إرسال السجل (Log) في روم السجلات المحدد
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
                
                print(f"تم إعطاء رتبة ({role.name}) ونشر السجل للعضو: {member.name}")
            else:
                print("خطأ: لم يتم العثور على رتبة الأوتو رول، تأكد من الـ ID.")
        except Exception as e:
            print(f"خطأ أثناء إعطاء رتبة الدخول أو إرسال السجل: {e}")

async def setup(bot):
    await bot.add_cog(AutoRole(bot))
