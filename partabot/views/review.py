from datetime import datetime

import discord
from .. import session, POST_CHANNEL, partabot_client
from ..modals import RefusedReasonForm

default_reasons = {
    'Manque de code':"Nous préférons mettre en avant des projets matures et aboutis, avec une quantité de code suffisante. Votre projet n'est ainsi pas assez gros à notre goût. Certes, cela est très bien de faire des projets, c'est une bonne façon d'apprendre la programmation, mais il faudrait peut-être l'épaissir un peu, ou attendre un plus gros projet, avant de le partager comme ça ^^.",
    'Projet non-open-source':"Le but du salon est de promouvoir l'open source, pas de faire de la publicité. Ainsi, nous préférons refuser les projets qui ne donnent pas un lien vers un github, gitlab, ou tout autre site destiné au partage de code.",
    'Projet Illegal':"Votre projet est non conformes aux règles de ce discord ou aux TOS de discord. Par conséquent, nous ne pouvons pas vous laisser poster ce projet dans le salon."
}


class DropdownReview(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Manque de code', description='', emoji='📝'),
            discord.SelectOption(label='Projet non-open-source', description='', emoji='🔒'),
            discord.SelectOption(label='Projet Illegal', description='', emoji='👮'),
            discord.SelectOption(label='Autre', description='', emoji='✒')
        ]
        super().__init__(placeholder='Refuser', options=options)

    async def callback(self, interaction: discord.Interaction):
        print(self.view.presentation.id, ": Denied")
        if self.values[0] == 'Autre':
            await interaction.response.send_modal(RefusedReasonForm(self.view.presentation))
        else:
            presentation_embed = self.view.presentation.embed('222222')
            reason_embed = discord.Embed(
                colour=int('ff2222', 16),
                title="Refus de votre présentation",
                description=f"Raison : {default_reasons[self.values[0]]}",
            )
            user = await partabot_client.fetch_user(self.view.presentation.author_id)
            await user.send(embeds=[presentation_embed, reason_embed])
        self.view.presentation.reviewed = True
        self.view.presentation.review_date = datetime.utcnow()
        self.view.presentation.accepted = False
        self.view.presentation.reviewed_by = interaction.user.id
        session.commit()
        embed = interaction.message.embeds[0]
        embed.colour = int("ff2222", 16)
        embed.set_footer(text=f"Refusé par {interaction.user.display_name}")
        embed.timestamp = self.view.presentation.review_date
        await interaction.message.edit(embed=embed, view=None)
        self.view.stop()


class Review(discord.ui.View):
    def __init__(self, presentation):
        super().__init__()
        self.presentation = presentation
        self.add_item(DropdownReview())

    @discord.ui.button(label='Accepter', style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(self.presentation.id, ": Accepted")
        self.presentation.reviewed = True
        self.presentation.review_date = datetime.utcnow()
        self.presentation.accepted = True
        self.presentation.reviewed_by = interaction.user.id
        session.commit()
        embed = interaction.message.embeds[0]
        embed.colour = int("22ff22", 16)
        embed.set_footer(text=f"Accepté par {interaction.user.display_name}")
        embed.timestamp = self.presentation.review_date
        await interaction.response.edit_message(embed=embed, view=None)
        embed.title = " ".join(embed.title.split()[1:])
        await partabot_client.get_channel(POST_CHANNEL).send(embed=embed)
        self.stop()
