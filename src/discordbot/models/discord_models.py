from typing import Annotated

from pydantic import BaseModel, Field


class DiscordUser(BaseModel):
    id: Annotated[str, Field(
        ...,
        description="The discord id of the user"
    )]
    username: Annotated[str, Field(
        ...,
        description="The username of the user, at the time of the event"
    )]

