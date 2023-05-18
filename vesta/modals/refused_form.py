import discord
import logging
import traceback

from .. import vesta_client, lang_file

logger = logging.getLogger(__name__)


class RefusedReasonForm(discord.ui.Modal, title=""):
    reason = discord.ui.TextInput(
        label="",
        style=discord.TextStyle.long
    )

    def __init__(self, presentation, interaction):
        logger.debug(f"RefusedReasonForm created for {interaction.user}")

        self.title = lang_file.get("denied_form", interaction.guild)
        self.reason.label = lang_file.get("denied_form_reason", interaction.guild)
        super().__init__()
        self.presentation = presentation

    async def on_submit(self, interaction: discord.Interaction):
        logger.debug(f"RefusedReasonForm submitted for {interaction.user}")

        presentation_embed = self.presentation.embed('222222')
        reason_embed = discord.Embed(
            colour=int('ff2222', 16),
            title=lang_file.get("denied_feedback_title", interaction.guild),
            description=lang_file.get("denied_feedback_content", interaction.guild) + f" {self.reason.value}",
        )
        user = await vesta_client.fetch_user(self.presentation.author_id)
        await user.send(embeds=[presentation_embed, reason_embed])
        await interaction.response.send_message(lang_file.get("denied_registered", interaction.guild), ephemeral=True)

    async def on_error(self, interaction, error):
        logger.error(traceback.format_exc())
        await interaction.response.send_message(lang_file.get("unexpected_error", interaction.guild), ephemeral=True)

