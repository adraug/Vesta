from discord import Embed
import sqlalchemy as db
from sqlalchemy.orm import relationship
from datetime import datetime

from . import Base


class Presentation(Base):
    __tablename__ = "presentation"

    id = db.Column(db.BigInteger, primary_key=True)
    creation_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(511))
    reviewed = db.Column(db.Boolean, default=False, nullable=False)
    reviewed_by = db.Column(db.BigInteger)
    review_date = db.Column(db.DateTime)
    accepted = db.Column(db.Boolean, default=False, nullable=False)

    author_id = db.Column(db.BigInteger, db.ForeignKey("user.id"), nullable=False)
    author = relationship("User", back_populates="presentations")

    def __repr__(self):
        return f"Presentation(id={self.id}, author={self.author}, title={self.title})"

    def embed(self, colour):
        presentation_embed = Embed(
            colour=int(colour, 16),
            title=f"[{self.id}] {self.title}",
            description=self.description,
            url=self.url
        )
        presentation_embed.set_author(name=self.author.name,
                                      icon_url=self.author.avatar_url)
        if self.image_url:
            presentation_embed.set_image(url=self.image_url)

        return presentation_embed


