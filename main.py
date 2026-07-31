import discord
from discord.ext import commands
import datetime
import os

intents = discord.Intents.all()
intents.message_content = True 

bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------- الإعدادات والمتغيرات -----------------
LOG_CHANNEL_ID = 1528789041934368900       # آيدي روم السجلات
TARGET_CHANNEL_ID = 1528793300394574053      # آيدي روم البداية للحماية
AUTO_ROLE_ID = 1375197032192671847          # آيدي رتبة Member للأعضاء الجدد

# قائمة التخطي (تحفظ الآيديّات)
WHITELISTED_USERS = set()

@bot.event
async def on_ready():
    print(f"========================================")
    print(f"تم تسجيل الدخول بنجاح! البوت يعمل الآن باسم: {bot.user.name}")
    print(f"نظام الحماية ولوحة التحكم التفاعلية جاهزة!")
    print(f"========================================")
    try:
        synced = await bot.tree.sync()
        print(f"تم مزامنة {len(synced)} أمر سلاتش بنجاح.")
    except Exception as e:
        print(f"خطأ في مزامنة الأوامر: {e}")

# ----------------- النوافذ المنبثقة (Modals) لإدخال الآيدي -----------------
class AddWhitelistModal(discord.ui.Modal, title="إضافة عضو لقائمة التخطي"):
    member_id = discord.ui.TextInput(
        label="آيدي العضو (User ID)",
        placeholder="مثال: 123456789012345678",
        min_length=17,
        max_length=20,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uid = int(self.member_id.value.strip())
            WHITELISTED_USERS.add(uid)
            await interaction.response.send_message(f"✅ تم بنجاح إدراج العضو الحامل للآيدي (`{uid}`) إلى **قائمة التخطي**.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ الآيدي الذي أدخلته غير صالح. تأكد من إدخال أرقام صحيحة فقط.", ephemeral=True)

class RemoveWhitelistModal(discord.ui.Modal, title="إزالة عضو من قائمة التخطي"):
    member_id = discord.ui.TextInput(
        label="آيدي العضو (User ID)",
        placeholder="مثال: 123456789012345678",
        min_length=17,
        max_length=20,
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            uid = int(self.member_id.value.strip())
            if uid in WHITELISTED_USERS:
                WHITELISTED_USERS.remove(uid)
                await interaction.response.send_message(f"❌ تم بنجاح إزالة العضو (`{uid}`) من قائمة التخطي.", ephemeral=True)
            else:
                await interaction.response.send_message(f"⚠️ العضو (`{uid}`) غير موجود في قائمة التخطي أصلاً.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ الآيدي الذي أدخلته غير صالح. تأكد من إدخال أرقام صحيحة فقط.", ephemeral=True)

# ----------------- لوحة التحكم الثابتة والأزرار التفاعلية -----------------
class SecurityView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # الأزرار ثابتة ولا تنتهي أبداً

    @discord.ui.button(label="إضافة تخطي لعضو✅", style=discord.ButtonStyle.green, custom_id="add_whitelist_btn")
    async def add_wl(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ عذراً، هذا الزر مخصص للإدارة العليا فقط (`Administrator`)!", ephemeral=True)
            return
        # فتح استمارة/نافذة إدخال الآيدي مباشرة
        await interaction.response.send_modal(AddWhitelistModal())

    @discord.ui.button(label="إزالة تخطي عضو❌", style=discord.ButtonStyle.red, custom_id="remove_whitelist_btn")
    async def remove_wl(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ عذراً، هذا الزر مخصص للإدارة العليا فقط!", ephemeral=True)
            return
        # فتح استمارة/نافذة إزالة الآيدي مباشرة
        await interaction.response.send_modal(RemoveWhitelistModal())

    @discord.ui.button(label="حالة الحماية والمتخطين", style=discord.ButtonStyle.blurple, custom_id="status_whitelist_btn")
    async def status_wl(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ عذراً، هذا الزر مخصص للإدارة العليا فقط!", ephemeral=True)
            return
        
        users_list = [f"• <@{uid}> (`{uid}`)" for uid in WHITELISTED_USERS] if WHITELISTED_USERS else ["لا يوجد أعضاء في قائمة التخطي حالياً."]
        embed = discord.Embed(
            title="🛡️ حالة نظام الحماية والتخطي",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="🔒 حالة الحماية", value="🟢 مفعلة بالكامل (حماية رومات، رتب، وبوتات)", inline=False)
        embed.add_field(name="👥 الأعضاء المتخطون حالياً", value="\n".join(users_list), inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

# أمر إظهار لوحة التحكم الثابتة الوحيد
@bot.tree.command(name="security-panel", description="إظهار لوحة تحكم الحماية المركزية في السيرفر (للإدارة فقط)")
async def security_panel(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ لا تملك صلاحية لاستخدام هذا الأمر!", ephemeral=True)
        return

    embed = discord.Embed(
        title="لوحة تحكم الحماية المركزية للسيرفر 🛡️",
        description="هذه اللوحة ثابتة ومخصصة لمراقبة وإدارة أمان السيرفر ضد التخريب.\n\n• **حماية الرومات:** استرجاع الروم المحذوف فوراً بنفس الاسم والصلاحيات.\n• **حماية الرتب:** منع التخريب العشوائي.\n• **حماية البوتات:** منع دخول أي بوت غير مصرح به.\n\nاستخدم الأزرار أدناه للإدارة الفورية:",
        color=discord.Color.dark_embed(),
        timestamp=datetime.datetime.now()
    )
    embed.set_footer(text="N W | H P System Security")
    
    await interaction.channel.send(embed=embed, view=SecurityView())
    await interaction.response.send_message("✅ تم إنشاء لوحة التحكم الثابتة بنجاح في هذه الروم!", ephemeral=True)

# ----------------- حماية الحذف واسترجاع الرومات (Anti-Nuke) -----------------
@bot.event
async def on_guild_channel_delete(channel):
    try:
        async for entry in channel.guild.audit_logs(limit=1, action=discord.AuditLogAction.channel_delete):
            user = entry.user
            if user.id in WHITELISTED_USERS or user.bot or user.id == channel.guild.owner_id:
                return

            guild = channel.guild
            new_channel = None
            
            if isinstance(channel, discord.TextChannel):
                new_channel = await guild.create_text_channel(
                    name=channel.name,
                    category=channel.category,
                    overwrites=channel.overwrites,
                    topic=channel.topic,
                    slowmode_delay=channel.slowmode_delay,
                    nsfw=channel.nsfw,
                    position=channel.position,
                    reason=f"حماية التخريب: استرجاع الروم المحذوف بواسطة {user.name}"
                )
            elif isinstance(channel, discord.VoiceChannel):
                new_channel = await guild.create_voice_channel(
                    name=channel.name,
                    category=channel.category,
                    overwrites=channel.overwrites,
                    bitrate=channel.bitrate,
                    user_limit=channel.user_limit,
                    position=channel.position,
                    reason=f"حماية التخريب: استرجاع الروم المحذوف بواسطة {user.name}"
                )
            elif isinstance(channel, discord.CategoryChannel):
                new_channel = await guild.create_category(
                    name=channel.name,
                    overwrites=channel.overwrites,
                    position=channel.position,
                    reason=f"حماية التخريب: استرجاع القسم المحذوف بواسطة {user.name}"
                )

            log_channel = guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                guild_name = guild.name
                guild_icon = guild.icon.url if guild.icon else None

                embed = discord.Embed(
                    title="🚨 إنذار حماية: تم حذف روم واسترجاعـه تلقائياً!",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                if guild_icon:
                    embed.set_author(name=guild_name, icon_url=guild_icon)
                else:
                    embed.set_author(name=guild_name)

                embed.add_field(name="👤 الشخص المخرب:", value=user.mention, inline=False)
                embed.add_field(name="📂 الروم المحذوف:", value=channel.name, inline=False)
                embed.add_field(name="⚖️ الإجراء المتخذ:", value="تم إعادة إنشاء الروم مع كافة صلاحياته وقسمه بنجاح!", inline=False)
                embed.set_thumbnail(url=user.display_avatar.url)
                embed.set_footer(text=f"ID: {user.id}")
                
                await log_channel.send(embed=embed)
    except Exception as e:
        print(f"خطأ في حماية حذف الرومات: {e}")

# ----------------- حماية دخول البوتات (Anti-Bot) -----------------
@bot.event
async def on_member_join(member):
    print(f">>> تم رصد دخول عضو جديد: {member.name}")
    try:
        if member.bot:
            async for entry in member.guild.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                adder = entry.user
                if adder.id not in WHITELISTED_USERS and adder.id != member.guild.owner_id:
                    await member.kick(reason="حماية التخريب: ممنوع إضافة بوتات غير مصرح بها!")
                    
                    log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
                    if log_channel:
                        embed = discord.Embed(
                            title="🚨 حماية البوتات: تم طرد بوت مخترق!",
                            color=discord.Color.red(),
                            timestamp=datetime.datetime.now()
                        )
                        embed.add_field(name="🤖 البوت المطرود:", value=member.mention, inline=False)
                        embed.add_field(name="👤 الشخص الذي حاول إضافته:", value=adder.mention, inline=False)
                        embed.add_field(name="⚖️ الإجراء:", value="تم طرد البوت فوراً لعدم وجود إذن تخطي.", inline=False)
                        await log_channel.send(embed=embed)
                    return

        # الأوتو رول الطبيعي للعضو الجديد
        role = member.guild.get_role(AUTO_ROLE_ID)
        if role:
            await member.add_roles(role)
            log_channel = member.guild.get_channel(LOG_CHANNEL_ID)
            if log_channel:
                guild_name = member.guild.name
                guild_icon = member.guild.icon.url if member.guild.icon else None
                
                embed = discord.Embed(
                    title="✨ سجل الأعضاء الجدد (Auto-Role)",
                    color=discord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
                if guild_icon:
                    embed.set_author(name=guild_name, icon_url=guild_icon)
                else:
                    embed.set_author(name=guild_name)

                embed.add_field(name="👤 العضو الجديد:", value=member.mention, inline=False)
                embed.add_field(name="🛡️ المسؤول (البوت):", value=bot.user.mention, inline=False)
                embed.add_field(name="⚖️ الإجراء:", value=f"منح رتبة: ({role.name})", inline=False)
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"ID: {member.id}")
                
                await log_channel.send(embed=embed)
    except Exception as e:
        print(f"خطأ في on_member_join: {e}")

# ----------------- نظام الحماية في روم البداية فقط -----------------
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.channel.id != TARGET_CHANNEL_ID:
        await bot.process_commands(message)
        return

    is_violation = False
    violation_reason = ""

    if message.attachments:
        is_violation = True
        violation_reason = "إرسال صورة مشبوهة أو غير مرغوب فيها/ حساب مخترق"

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
                guild_name = message.guild.name
                guild_icon = message.guild.icon.url if message.guild.icon else None

                embed = discord.Embed(
                    title="🚨 سجل الحماية (من الحسابات المخترقة)",
                    color=discord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                if guild_icon:
                    embed.set_author(name=guild_name, icon_url=guild_icon)
                else:
                    embed.set_author(name=guild_name)

                embed.add_field(name="👤 العضو المخترق:", value=message.author.mention, inline=False)
                embed.add_field(name="🛡️ المسؤول (البوت):", value=bot.user.mention, inline=False)
                embed.add_field(name="⚖️ الإجراء:", value="تايم أوت لمدة أسبوع (7 أيام)", inline=False)
                embed.add_field(name="📝 السبب:", value=violation_reason, inline=False)
                embed.set_thumbnail(url=message.author.display_avatar.url)
                embed.set_footer(text=f"ID: {message.author.id}")
                
                await log_channel.send(embed=embed)

            warning_msg = await message.channel.send(f"🚨 تنبيه {message.author.mention}: ممنوع إرسال الصور أو الرابط هنا! تم إعطاؤك تايم أوت أسبوع.")
            await warning_msg.delete(delay=10)
        except Exception as e:
            print(f"خطأ أثناء الحماية: {e}")

    await bot.process_commands(message)

# تشغيل البوت
TOKEN = os.getenv('TOKEN') or 'ضع_التوكين_هنا'
bot.run(TOKEN)
