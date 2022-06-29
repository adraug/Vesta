import discord
from discord import app_commands

from typing import Optional

from .. import partabot_client, GUILD, session
from ..modals import PresentationForm
from ..tables import Presentation, select, or_, User


@partabot_client.tree.command(description="Submit a presentation")
async def presentation(interaction: discord.Interaction):
    r = select(User).where(User.id == interaction.user.id)
    author = session.scalar(r)
    if author and author.presentations_banned:
        return await interaction.response.send_message(
            "Vous n'avez pas les permissions soumettre une présentation",
            ephemeral=True)
    await interaction.response.send_modal(PresentationForm())


@app_commands.guild_only()
@app_commands.default_permissions(ban_members=True)
class PresentationManage(app_commands.Group, name="presentationmanage", description="Nickname manager"):

    async def on_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "You don't have the permissions to use this command", ephemeral=True)
        else:
            print(error)
            await interaction.response.send_message("Une erreur s'est produite", ephemeral=True)


presentation_manage = PresentationManage()


@presentation_manage.command(description="Show a presentation")
@app_commands.describe(research="Presentation's Id or Author's Id")
async def show(interaction: discord.Interaction, research: Optional[str] = None, user: Optional[discord.Member] = None):
    if not (research or user):
        return await interaction.response.send_message(
            "Merci de mettre au moins un des paramètres", ephemeral=True)
    if user:
        r = select(Presentation).where(Presentation.author_id == user.id)
    else:
        if not research.isdecimal() or int(research) > 2 ** 63 - 1:
            return await interaction.response.send_message(
                content="Merci d'entrez un nombre valide",
                ephemeral=True)
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


@presentation_manage.command(description="Ban a user from submitting a presentation")
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
    author.presentations_banned = True
    session.commit()

    await interaction.response.send_message(
        content=f"{user} a bien été banni des présentations")


@presentation_manage.command(description="Unban a user from submitting a presentation")
@app_commands.describe(user="The user to unban")
async def unban(interaction: discord.Interaction, user: discord.Member):
    r = select(User).where(User.id == user.id)
    author = session.scalar(r)
    if not (author and author.presentations_banned):
        return await interaction.response.send_message(
            content=f"{user} n'est pas banni des présentations")
    author.presentations_banned = False
    session.commit()

    await interaction.response.send_message(
        content=f"{user} a bien été débanni des présentations")


@presentation_manage.command(description="Show the banlist")
@app_commands.describe(page="The page")
async def banlist(interaction: discord.Interaction, page: Optional[int] = 0):
    r = select(User).where(User.presentations_banned == True).offset(100 * page).fetch(100)
    banned_users = session.scalars(r)

    banlist = ""
    for user in banned_users:
        banlist += f"{user.name}#{user.discriminator}\n"

    banned_embed = discord.Embed(title="Membres bannis des présentations", description=banlist)
    banned_embed.set_footer(text=f"Page {page}")

    await interaction.response.send_message(embed=banned_embed)


partabot_client.tree.add_command(presentation_manage, guild=GUILD)
