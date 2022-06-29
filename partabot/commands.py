import discord
from discord import app_commands

import re
from typing import Optional

from . import partabot_client, GUILD, session
from .modals import PresentationForm
from .tables import Presentation, select, or_, User

regex_name = r"[A-Za-z0-9À-ÿ ]{3}[A-Za-z0-9À-ÿ\/.+=()\[\]{}&%*!:;,?§<>_ -|#]{0,29}"

@partabot_client.tree.command(description="Submit a presentation")
async def presentation(interaction: discord.Interaction):
    await interaction.response.send_modal(PresentationForm())


@partabot_client.tree.command(description="Review a presentation", guild=GUILD)
@app_commands.describe(
    research="Presentation's Id or Author's Id"
)
async def show_presentation(interaction: discord.Interaction, research: str):
    if not research.isdecimal() or int(research) > 2**63-1:
        return await interaction.response.send_message(
            content="Merci d'entrez un nombre valide",
            ephemeral=True,
        )
    r = select(Presentation).where(or_(Presentation.id == research, Presentation.author_id == research))
    presentations = session.scalars(r).all()
    if not len(presentations):
        return await interaction.response.send_message(
            content="Aucun résultat n'a pu être trouvé",
            ephemeral=True,
        )
    if len(presentations) == 1:
        presentation = presentations[0]
        embed = presentation.embed('222222')
        return await interaction.response.send_message(embed=embed)
    embed = discord.Embed(
        colour=int('222222', 16),
        title="Résultats de la recherche par utilisateur"
    )
    for presentation in presentations:
        emoji = '🕑'
        if presentation.reviewed:
            emoji = ['❌', '✅'][presentation.accepted]
        embed.add_field(name=f"{presentation.id} : {emoji}", value=presentation.title)
    return await interaction.response.send_message(embed=embed)

class Nick(app_commands.Group, name="nickname", description="Nickname manager"):

    async def on_error(self, interaction: discord.Interaction, error):
        print(error)
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "You don't have the permissions to use this command", ephemeral=True)
        elif isinstance(error, app_commands.errors.BotMissingPermissions):
            await interaction.response.send_message(
                "Malheureusement, le bot n'a pas les permissions suffisantes pour changer votre pseudo",
                ephemeral=True)

nick = Nick()

@nick.command(description="Change your pseudonyme")
@app_commands.describe(name="Your future username")
@app_commands.checks.bot_has_permissions(manage_nicknames=True)
async def set(interaction: discord.Interaction, name:str):
    r = select(User).where(User.id == interaction.user.id)
    author = session.scalar(r)
    if author and author.nicknames_banned:
        return await interaction.response.send_message(
            "Vous n'avez pas les permissions pour vous rename",
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

@nick.command(description="Ban a user from using the nickname command")
@app_commands.describe(user="The user to ban")
@app_commands.default_permissions(manage_nicknames=True)
@app_commands.checks.has_permissions(manage_nicknames=True)
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

@nick.command(description="Unban a user from using the nickname command")
@app_commands.describe(user="The user to unban")
@app_commands.default_permissions(manage_nicknames=True)
@app_commands.checks.has_permissions(manage_nicknames=True)
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

@nick.command(description="Show the banlist")
@app_commands.describe(page="The page")
@app_commands.default_permissions(manage_nicknames=True)
@app_commands.checks.has_permissions(manage_nicknames=True)
async def banlist(interaction: discord.Interaction, page: Optional[int] = 0):

    r = select(User).where(User.nicknames_banned == True).offset(100 * page).fetch(100)
    banned_users = session.scalars(r)

    banlist = ""
    for user in banned_users:
        banlist += f"{user.name}#{user.discriminator}\n"

    banned_embed = discord.Embed(title="Membres bannis", description=banlist)
    banned_embed.set_footer(text=f"Page {page}")

    await interaction.response.send_message(embed=banned_embed)


partabot_client.tree.add_command(nick, guild=GUILD)