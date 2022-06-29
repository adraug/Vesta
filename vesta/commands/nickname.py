import re
from typing import Optional

import discord
from discord import app_commands

from .. import partabot_client, session, GUILD
from ..tables import User, select

regex_name = r"[A-Za-z0-9À-ÿ ]{3}[A-Za-z0-9À-ÿ\/.+=()\[\]{}&%*!:;,?§<>_ -|#]{0,29}"


@partabot_client.tree.command(description="Change your pseudonyme")
@app_commands.guild_only()
@app_commands.describe(name="Your future username")
@app_commands.checks.bot_has_permissions(manage_nicknames=True)
async def nickname(interaction: discord.Interaction, name: str):
    r = select(User).where(User.id == interaction.user.id)
    author = session.scalar(r)
    if author and author.nicknames_banned:
        return await interaction.response.send_message(
            "Vous avez été banni du système de rename",
            ephemeral=True)
    if not re.match(regex_name, name):
        response_embed = discord.Embed(color=int("FF4444", 16), title="⚠️ Pseudo incorrect !",
                                       description="Ce nom n'est pas valide," +
                                                   f"merci d'entrer un nom validant la regex suivante : `{regex_name}`")
        return await interaction.response.send_message(embed=response_embed, ephemeral=True)

    if isinstance(interaction.user, discord.Member):
        await interaction.user.edit(nick=name)
        await interaction.response.send_message(
            content="Votre pseudo à été changé avec succès !", ephemeral=True)
    else:
        await interaction.response.send_message(
            content="Merci de faire cette commande dans une guilde", ephemeral=True)


@nickname.error
async def nickname_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.errors.BotMissingPermissions):
        await interaction.response.send_message(
            "Malheureusement, le bot n'a pas les permissions suffisantes pour changer votre pseudo",
            ephemeral=True)
    else:
        print(error)
        await interaction.response.send_message("Une erreur s'est produite", ephemeral=True)


@app_commands.guild_only()
@app_commands.default_permissions(manage_nicknames=True)
class NickManage(app_commands.Group, name="nickmanage", description="Nickname manager"):

    async def on_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "You don't have the permissions to use this command", ephemeral=True)
        else:
            print(error)
            await interaction.response.send_message("Une erreur s'est produite", ephemeral=True)


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
        content=f"{user} a bien été banni de la commande nickname")


@nick_manage.command(description="Unban a user from using the nickname command")
@app_commands.describe(user="The user to unban")
async def unban(interaction: discord.Interaction, user: discord.Member):
    r = select(User).where(User.id == user.id)
    author = session.scalar(r)
    if not (author and author.nicknames_banned):
        return await interaction.response.send_message(
            content=f"{user} n'est pas banni de la commande nickname")
    author.nicknames_banned = False
    session.commit()

    await interaction.response.send_message(
        content=f"{user} a bien été débanni de la commande nickname")


@nick_manage.command(description="Show the banlist")
@app_commands.describe(page="The page")
async def banlist(interaction: discord.Interaction, page: Optional[int] = 0):
    r = select(User).where(User.nicknames_banned == True).offset(100 * page).limit(100)
    banned_users = session.scalars(r)

    banlist = ""
    for user in banned_users:
        banlist += f"<@{user.id}>\n"

    banned_embed = discord.Embed(title="Membres bannis du nickname", description=banlist)
    banned_embed.set_footer(text=f"Page {page}")

    await interaction.response.send_message(embed=banned_embed,
                                            allowed_mentions=discord.AllowedMentions().none())


partabot_client.tree.add_command(nick_manage, guild=GUILD)
