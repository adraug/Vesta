import re
from typing import Optional

import discord
from discord import app_commands

from .. import vesta_client, session, lang
from ..tables import User, select

regex_name = r"[A-Za-z0-9À-ÿ ]{3}[A-Za-z0-9À-ÿ\/.+=()\[\]{}&%*!:;,?§<>_ -|#]{0,29}"


@vesta_client.tree.command(description="Change your pseudonyme")
@app_commands.guild_only()
@app_commands.describe(name="Your future username")
@app_commands.checks.bot_has_permissions(manage_nicknames=True)
async def nickname(interaction: discord.Interaction, name: str):
    r = select(User).where(User.id == interaction.user.id)
    author = session.scalar(r)
    if author and author.nicknames_banned:
        return await interaction.response.send_message(
            lang.get("nickname_banned", interaction.guild),
            ephemeral=True)

    if not interaction.user.guild_permissions.manage_nicknames and not re.match(regex_name, name):
        response_embed = discord.Embed(color=int("FF4444", 16), title=lang.get("nickname_incorrect_title", interaction.guild),
                                       description=lang.get("nickname_incorrect_description", interaction.guild) + f"`{regex_name}`")
        return await interaction.response.send_message(embed=response_embed, ephemeral=True)

    await interaction.user.edit(nick=name)
    await interaction.response.send_message(
        content=lang.get("nickname_changed", interaction.guild), ephemeral=True)


@nickname.error
async def nickname_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.BotMissingPermissions):
        await interaction.response.send_message(
            lang.get("bot_permissions_error", interaction.guild) + f" {', '.join(error.missing_permissions)}",
            ephemeral=True)
    else:
        print(error)
        await interaction.response.send_message(lang.get("unexpected_error", interaction.guild), ephemeral=True)


@app_commands.guild_only()
@app_commands.default_permissions(manage_nicknames=True)
class NickManage(app_commands.Group, name="nickmanage", description="Nickname manager"):

    async def on_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                lang.get("permissions_error", interaction.guild), ephemeral=True)
        else:
            print(error)
            await interaction.response.send_message(lang.get("unexpected_error", interaction.guild), ephemeral=True)


nick_manage = NickManage()


@nick_manage.command(description="Ban a user from using the nickname command")
@app_commands.describe(user="The user to ban")
async def ban(interaction: discord.Interaction, user: discord.Member):
    r = select(User).where(User.id == user.id)
    author = session.scalar(r)
    if not author:
        author = User(
            id=user.id,
            name=user.display_name,
            avatar_url=user.display_avatar.url
        )
        session.add(author)
    author.nicknames_banned = True
    session.commit()

    await interaction.response.send_message(
        content=f"{user} " + lang.get("nickname_ban", interaction.guild))


@nick_manage.command(description="Unban a user from using the nickname command")
@app_commands.describe(user="The user to unban")
async def unban(interaction: discord.Interaction, user: discord.Member):
    r = select(User).where(User.id == user.id)
    author = session.scalar(r)
    if not (author and author.nicknames_banned):
        return await interaction.response.send_message(
            content=f"{user} " + lang.get("nickname_not_banned", interaction.guild))
    author.nicknames_banned = False
    session.commit()

    await interaction.response.send_message(
        content=f"{user} " + lang.get("nickname_unban", interaction.guild))


@nick_manage.command(description="Show the banlist")
@app_commands.describe(page="The page")
async def banlist(interaction: discord.Interaction, page: Optional[int] = 0):
    r = select(User).where(User.nicknames_banned == True).offset(100 * page).limit(100)
    banned_users = session.scalars(r)

    ban_list = ""
    for user in banned_users:
        ban_list += f"<@{user.id}>\n"

    banned_embed = discord.Embed(title=lang.get("nickname_list_title", interaction.guild), description=ban_list)
    banned_embed.set_footer(text=lang.get("list_page", interaction.guild) + f" {page}")

    await interaction.response.send_message(embed=banned_embed,
                                            allowed_mentions=discord.AllowedMentions().none())


vesta_client.tree.add_command(nick_manage)
