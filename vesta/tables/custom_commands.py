import sqlalchemy as db
from discord import Embed
from sqlalchemy.orm import relationship

from . import Base


class CustomCommand(Base):
    __tablename__ = "custom_commands"

    guild_id = db.Column(db.BigInteger, nullable=False)
    keyword = db.Column(db.String(32), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    source_url = db.Column(db.String(511))
    image_url = db.Column(db.String(511))
    colour = db.Column(db.Integer)

    author_id = db.Column(db.BigInteger, db.ForeignKey("user.id"), nullable=False)
    author = relationship("User")

    db.PrimaryKeyConstraint(guild_id, keyword)

    def __repr__(self):
        return f"Custom Command (guild_id={self.guild_id}, keyword={self.keyword}, author={self.author}, title={self.title})"

    def embed(self):
        custom_embed = Embed(
            colour=self.colour,
            title=self.title,
            description=self.content
        )
        custom_embed.set_author(name=self.author.name,
                                icon_url=self.author.avatar_url)
        if self.source_url:
            custom_embed.url = self.source_url
        if self.image_url:
            custom_embed.set_image(url=self.image_url)

        return custom_embed
