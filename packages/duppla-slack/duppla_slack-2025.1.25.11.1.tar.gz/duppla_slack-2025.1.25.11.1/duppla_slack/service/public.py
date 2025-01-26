import json
from collections.abc import Iterator
from typing import Any, cast, overload
from warnings import warn

import requests
from slack_sdk import WebClient as SlackLibClient

from duppla_slack.constants.channels import AIRFLOW_CHANNEL
from duppla_slack.constants.templates import Filetype
from duppla_slack.models import (
    Bookmark,
    EphemeralMessage,
    LongMessage,
    Message,
    ScheduledMessage,
    SlackApiError,
    SlackProfile,
    SlackResponse,
)


class SlackService(SlackLibClient):
    """
    This class extends the SlackLibClient and provides methods for sending messages, updating messages, sending ephemeral messages, scheduling messages, and more.
    It simplifies the interaction with Slack by offering higher-level abstractions over the raw API calls, making it easier to perform common tasks such as sending messages, managing channels, and handling user interactions.

    The SlackService class is designed to be flexible and extensible, allowing us, as the owners, to customize and extend its functionality as needed.
    It includes various utility functions that cover a wide range of use cases, from basic message sending to more complex operations like scheduling messages and managing channel memberships.

    Additionally, the class provides overloads for certain methods to handle different types of inputs, ensuring that the correct API calls are made based on the provided arguments.
    This helps to reduce errors and improve the overall developer experience when working with the Slack API.

    For more detailed information on the available methods and their usage, please refer to the official Slack API documentation: https://api.slack.com/
    SlackService is a wrapper around the Slack API that provides utility functions for interacting with Slack.

    Examples:
    ```python
    from duppla_slack import SlackService

    slack_service = SlackService(token="xox")

    # Send a simple message
    slack_service.send_msg_(text="Hello, world!", channel="C1234567890")

    # Sends a simple message using the Message object
    from duppla_slack.models import Message

    slack_service.send_msg(Message(text="Hello, world!", channel="C1234567890"))

    # Get channel information by ID
    channel_info = slack_service.get_channel(channel_id="C1234567890")

    # Get channel information by name
    channel_info = slack_service.get_channel(channel_name="general")

    # Get a list of all channels
    channels = slack_service.get_channels()

    # Get a list of all members
    members = slack_service.get_members()
    ```

    """

    def __init__(self, token: str):
        super().__init__(token=token)

    @overload
    def send_msg_(
        self,
        *,
        text: str,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: str | None = None,
        reply_broadcast: bool = False,
        **kwargs: Any,  # attachments, blocks or metadata
    ) -> SlackResponse:
        """
        Utility function that sends a message to a Slack channel.
        If the channel is a user ID, the message will be sent as a direct message to that user.
        If the thread_ts is set, the message will be sent as a reply to the specified thread and if the reply_broadcast is set to True, the message will also be sent to the entire channel.

        Args:
            text (str): The text of the message.
            channel (str): The ID of the channel to send the message to. Default is the AIRFLOW_CHANNEL.
            thread_ts (str): The timestamp of the parent message to reply to.
            reply_broadcast (bool): Whether to send the message to the entire channel. Default is False.
            **kwargs: Additional arguments for the message. \
                <However, discouraged, use `send_msg(message=Message(...))` instead>\
                attachments (list[Attatchments]), blocks (list[dict[str, Any]]), metadata (MessageMetadata)

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """

    @overload
    def send_msg_(
        self,
        *,
        content: str,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: str | None = None,
        reply_broadcast: bool = False,
        initial_comment: str | None = None,
        snippet_type: Filetype = "auto",
        **kwargs: Any,
    ) -> SlackResponse:
        """
        Utility function that sends a long message to a Slack channel.
        The message is sent as a file, to avoid the truncate originated from the 4000 characters limit of the text field.

        Args:
            content (str): The text of the message.
            channel (str): The ID of the channel to send the message to. Default is the AIRFLOW_CHANNEL.
            thread_ts (str): The timestamp of the parent message to reply to.
            reply_broadcast (bool): Whether to send the message to the entire channel. Default is False.
            initial_comment (str): The text of the initial comment.
            snippet_type (str): The type of the snippet. Default is None.

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.upload  [Deprecated but shows the use of files.uploadv2]
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """

    def send_msg_(
        self,
        *,
        text: str,
        channel: str = AIRFLOW_CHANNEL,
        thread_ts: str | None = None,
        reply_broadcast: bool = False,
        initial_comment: str | None = None,
        snippet_type: Filetype = "auto",
        **kwargs: Any,
    ) -> SlackResponse:
        kwargs.update(
            {
                "text": text,
                "channel": channel,
                "thread_ts": thread_ts,
                "reply_broadcast": reply_broadcast,
                "initial_comment": initial_comment,
                "snippet_type": snippet_type,
            }
        )
        if "attachments" in kwargs or "blocks" in kwargs:
            warn("Use the `send_msg` method for rich content messages")

        if "content" in kwargs:
            result = self.files_upload_v2(**kwargs)
        elif "text" in kwargs:
            result = self.chat_postMessage(**kwargs)
        else:
            raise ValueError("Invalid message type")
        return SlackResponse.from_sdk(result)

    @overload
    def send_msg(self, message: Message) -> SlackResponse:
        """
        Sends a message to a Slack channel.
        If the channel is a user ID, the message will be sent as a direct message to that user.
        If the thread_ts is set, the message will be sent as a reply to the specified thread and if the reply_broadcast is set to True, the message will also be sent to the entire channel.

        Args:
            message (Message): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """

    @overload
    def send_msg(self, message: LongMessage) -> SlackResponse:
        """
        Sends a long message to a Slack channel.
        The message is sent as a file, to avoid the truncate originated from the 4000 characters limit of the text field.

        Args:
            message (LongMessage): The message to send.

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.upload  [Deprecated but shows the use of files.uploadv2]
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """

    def send_msg(self, message: Message | LongMessage) -> SlackResponse:
        if isinstance(message, LongMessage):
            result = self.files_upload_v2(**message.model_dump(exclude_none=True))
        else:
            result = self.chat_postMessage(**message.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(result)

    def update_message(
        self,
        *,
        channel: str,
        timestamp: str,
        text: str,
        **kwargs: Any,
    ) -> SlackResponse:
        """
        Updates message in a slack channel
        :param channel: the channel id where the message is located.
        :param timestamp: the timestamp of the message to update. This is used to identify the message to be updated (like an id).
        :param text: the new text for the message.
        :param blocks: the new blocks for the message, provides the new structured content for the message.
        :return: The updated message response.
        """
        kwargs.update(
            {
                "channel": channel,
                "ts": timestamp,
                "text": text,
            }
        )
        result = self.chat_update(**kwargs)
        return SlackResponse.from_sdk(result)

    update_msg = update_message

    def send_ephemeral_(
        self,
        *,
        user: str,
        channel: str = AIRFLOW_CHANNEL,
        text: str,
        thread_ts: str | None = None,
        reply_broadcast: bool = False,
        **kwargs: Any,  # attachments or blocks
    ) -> SlackResponse:
        """
        Utility function that sends an ephemeral message to a user in a Slack channel.

        Args:
            user (str): The ID of the user to send the message to.
            channel (str): The ID of the channel to send the message to.
            text (str): The text of the message.
            **kwargs: Additional arguments for the message. It can be attachments (list[Attatchments]) or blocks (list[dict[str, Any]]) <However, discouraged, use `send_ephemeral(message=EphemeralMessage(...))` instead>.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postEphemeral
        """
        result = self.chat_postEphemeral(
            user=user,
            channel=channel,
            text=text,
            thread_ts=thread_ts,
            reply_broadcast=reply_broadcast,
            **kwargs,
        )
        return SlackResponse.from_sdk(result)

    def send_ephemeral(self, message: EphemeralMessage) -> SlackResponse:
        """
        Sends an ephemeral message to a user in a Slack channel.

        Args:
            message (EphemeralMessage): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postEphemeral
        """
        result = self.chat_postEphemeral(**message.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(result)

    def send_scheduled_(
        self,
        *,
        post_at: int,
        channel: str = AIRFLOW_CHANNEL,
        text: str,
        thread_ts: str | None = None,
        reply_broadcast: bool = False,
        **kwargs: Any,
    ) -> SlackResponse:
        """
        Utility function that sends a scheduled message to a Slack channel.

        Args:
            post_at (int): The timestamp of the scheduled message.
            channel (str): The ID of the channel to send the message to.
            text (str): The text of the message.
            **kwargs: Additional arguments for the message. It can be attachments (list[Attatchments]) or blocks (list[dict[str, Any]]) <However, discouraged, use `send_scheduled(message=ScheduledMessage(...))` instead>.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.scheduleMessage
        """
        result = self.chat_scheduleMessage(
            post_at=post_at,
            channel=channel,
            text=text,
            thread_ts=thread_ts,
            reply_broadcast=reply_broadcast,
            **kwargs,
        )
        return SlackResponse.from_sdk(result)

    def send_scheduled(self, message: ScheduledMessage) -> SlackResponse:
        """
        Sends a scheduled message to a Slack channel.

        Args:
            message (ScheduledMessage): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.scheduleMessage
        """
        result = self.chat_scheduleMessage(**message.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(result)

    def send_and_pin_msg_(self, **kwargs: Any) -> SlackResponse:
        """
        Utility function that sends a message to a Slack channel and pins it.

        Args:
            **kwargs: The arguments for the message. It can be attachments (list[Attatchments]) or blocks (list[dict[str, Any]]) <However, discouraged, use `send_and_pin_msg(message=Message(...))` instead>.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """
        result = self.send_msg_(**kwargs)
        result += SlackResponse.from_sdk(
            self.pins_add(
                channel=kwargs.get("channel", AIRFLOW_CHANNEL),
                timestamp=result["ts"],
            )
        )
        return result

    def send_and_pin_msg(self, message: Message) -> SlackResponse:
        """
        Sends a message to a Slack channel and pins it.

        Args:
            message (Message): The message to send.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/chat.postMessage
        """
        result = self.send_msg(message)
        result += SlackResponse.from_sdk(
            self.pins_add(
                channel=message.channel,
                timestamp=result["ts"],
            )
        )
        return result

    def bookmark_add_(
        self,
        *,
        channel_id: str,
        title: str,
        type: str,
        **bookmark: Any,
    ) -> SlackResponse:
        """
        Utility function to add a bookmark without having to create a Bookmark object.

        Args:
            *bookmark: The bookmark arguments to add. (channel)

        Returns:
            dict: The response from the Slack API.
        """
        bookmark.update(
            {
                "channel_id": channel_id,
                "title": title,
                "type": type,
            }
        )
        result = self.bookmarks_add(**bookmark)
        return SlackResponse.from_sdk(result)

    def bookmark_add(self, bookmark: Bookmark) -> SlackResponse:
        """
        Adds a new bookmark to a Slack channel.

        Args:
            bookmark (Bookmark | None): The bookmark object to add. If None, a new bookmark will be created using the bookmark_kwargs.

        Returns:
            dict: The response from the Slack API.
        """
        result = self.bookmarks_add(**bookmark.model_dump(exclude_none=True))
        return SlackResponse.from_sdk(result)

    def send_image(
        self,
        *,
        channel: str,
        image: bytes,
        image_name: str,
        image_extension: str,
        message: str,
        thread_ts: str | None = None,
        **_,  # Is for ignoring the rest of the named arguments
    ) -> str:
        """
        This functions first uploads an image to slack and then sends it to a channel.
        NOTE: The bot must be in the channel to send the image.

        Args:
            channel (str): the slack channel id
            image (bytes): the image
            image_name (str): the image name
            image_extension (str): the image extension
            thread_ts (str): the thread timestamp
            message (str): the message to send with the image

        > Check the official documentation of the Slack API for more information:
            > https://api.slack.com/methods/files.getUploadURLExternal
            > https://api.slack.com/methods/files.completeUploadExternal
        """

        def _upload_image(upload_url: str, image: bytes, image_name: str) -> None:
            """
            Files are processed asynchronously via a job handler.
            Files can be sent as raw bytes or can be multipart form encoded.
            Slack will return HTTP 200 if the upload is successful; a non-200 response indicates a failure.
            > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/files.getUploadURLExternal
            """
            post_response = requests.post(upload_url, data=image)
            try:
                post_response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise SlackApiError(
                    message=f"Error uploading image {image_name} to slack, error: {e.response.text}",
                    response=e.response,
                )

        try:
            # First, get the upload URL
            upload_url_external = self.files_getUploadURLExternal(
                filename=f"{image_name}.{image_extension}", length=len(image)
            )

            upload_url = cast(str, upload_url_external["upload_url"])

            # Second, upload a file by making a POST request to the upload URL.
            _upload_image(upload_url, image, image_name)

            # Third, complete the upload and send the image to the channel
            complete_upload = self.files_completeUploadExternal(
                files=[{"id": upload_url_external["file_id"], "title": image_name}],
                channel_id=channel,
                initial_comment=message,
                thread_ts=thread_ts,
            )

            return complete_upload["files"][0]["id"]  # pyright: ignore[reportUnknownVariableType]
        except SlackApiError as e:
            raise e
        except Exception as e:
            raise SlackApiError(message="Error uploading image", response=str(e))

    def crear_canal(self, name: str, is_private: bool = False) -> SlackResponse:
        """
        Creates a new channel.

        Args:
            name (str): The name of the channel.
            is_private (bool): Whether the channel is private. Default is False.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.create
        """
        result = self.conversations_create(
            name=name,
            is_private=is_private,
        )
        return SlackResponse.from_sdk(result)

    create_channel = crear_canal

    @overload
    def get_channel(
        self,
        *,
        channel_id: str,
        include_num_members: bool = False,
        raise_exception: bool = False,
    ) -> dict[str, Any] | None:
        """
        Gets information about a channel.

        Args:
            channel_id (str): The ID of the channel.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.info
        """

    @overload
    def get_channel(
        self,
        *,
        channel_name: str,
        include_num_members: bool = False,
        raise_exception: bool = False,
    ) -> dict[str, Any] | None:
        """
        Gets information about a channel.

        Args:
            channel_name (str): The name of the channel.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.info
        """

    def get_channel(
        self,
        *,
        channel_id: str | None = None,
        channel_name: str | None = None,
        include_num_members: bool = False,
        raise_exception: bool = False,
    ) -> dict[str, Any] | None:
        if not channel_id and not channel_name:
            raise ValueError("Either channel_id or channel_name must be provided")

        if channel_id:
            result = self.conversations_info(
                channel=channel_id,
                include_num_members=include_num_members,
            ).data
            if not isinstance(result, dict):
                raise TypeError("Invalid response from Slack API")
        else:
            result = next(
                (
                    channel
                    for channel in self._get_channels()
                    if channel["name"] == channel_name
                ),
                None,
            )
            if raise_exception and not result:
                raise ValueError(f"Channel with name {channel_name} not found")

        return result

    def _get_channels(self) -> Iterator[dict[str, Any]]:
        """
        Lazy function that gets a list of all channels in the workspace.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.list
        """
        scope = "public_channel,private_channel"
        result = self.conversations_list(types=scope, limit=300)
        yield from result["channels"]
        while next_c := cast(str | None, result["response_metadata"]["next_cursor"]):
            result = self.conversations_list(types=scope, cursor=next_c, limit=300)
            yield from result["channels"]

    def get_channels(self) -> list[dict[str, Any]]:
        """
        Gets a list of all channels in the workspace.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.list
        """
        return [channel for channel in self._get_channels()]

    def get_channel_id(self, channel_name: str) -> str | None:
        """
        Gets the channel ID by channel name.

        Args:
            channel_name (str): The name of the channel.
        """
        channel = self.get_channel(channel_name=channel_name)
        return channel["id"] if channel else None

    channel_exists = get_channel_id

    def get_channel_name(self, channel_id: str) -> str | None:
        """
        Gets the channel name by channel ID.

        Args:
            channel_id (str): The ID of the channel.
        """
        channel = self.get_channel(channel_id=channel_id)
        return channel["name"] if channel else None

    def upsert_channel(self, name: str, is_private: bool = False) -> str:
        """
        Creates a new channel if it does not exist, otherwise returns the ID of the existing channel.

        Args:
            name (str): The name of the channel.
            is_private (bool): Whether the channel is private. Default is False.
        """
        c_id = self.get_channel_id(name)
        if c_id:
            return c_id
        else:
            return self.crear_canal(name=name, is_private=is_private)["channel"]["id"]

    def invitar_canal(self, channel: str, *users: str) -> dict[str, Any]:
        """
        Invites users to a channel.

        Args:
            channel (str): The ID of the channel.
            *users (str): The IDs of the users to invite.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.invite
        """
        assert users, "At least one user must be provided"
        try:
            return self.conversations_invite(channel=channel, users=users).data  # pyright: ignore[reportReturnType]
        except SlackApiError as e:
            e.response = cast(dict[str, Any], e.response)
            if e.response["error"] in ("already_in_channel", "cant_invite"):
                return e.response
            raise SlackApiError(
                message="Error inviting users to channel",
                response=e.response,
            )

    invite_channel = invitar_canal

    def uninvitar_canal(self, channel: str, *users: str) -> list[dict[str, Any]]:
        """
        Uninvites (kicks) users from a channel.

        Args:
            channel (str): The ID of the channel.
            *users (str): The IDs of the users to uninvite.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/conversations.kick
        """
        assert users, "At least one user must be provided"

        results: list[dict[str, Any]] = []
        for user in users:
            try:
                result = self.conversations_kick(channel=channel, user=user).data
                if isinstance(result, bytes):
                    result = json.loads(result)
                results.append(cast(dict[str, Any], result))
            except SlackApiError as e:
                e.response = cast(dict[str, Any], e.response)
                if e.response["error"] not in ("cant_kick_self", "not_in_channel"):
                    results.append(e.response)
                else:
                    raise SlackApiError(
                        message="Error uninviting users from channel",
                        response=e.response,
                    )
        return results

    uninvite_channel = uninvitar_canal
    kick_channel = uninvitar_canal

    def get_members(self, exclude_bots: bool = True) -> dict[str, SlackProfile]:
        """
        Gets a list of all users in the workspace.

        Args:
            exclude_bots (bool): Whether to exclude bots. Default is True.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.list
        """
        return {
            member["id"]: SlackProfile(
                member["profile"]
                | {"is_bot": member["is_bot"] or member["id"] == "USLACKBOT"}
            )
            for member in self._get_users()
            if not member["deleted"]
            and not (exclude_bots and (member["is_bot"] or member["id"] == "USLACKBOT"))
        }

    def get_users_id_name(self, exclude_bots: bool = True) -> dict[str, str]:
        """
        Retrieves a dictionary of Slack user IDs and names. Previously known as get_users_id
        """
        return {
            user["id"]: user["name"]
            for user in self._get_users()
            if not user["deleted"]
            and not (exclude_bots and (user["is_bot"] or user["id"] == "USLACKBOT"))
        }

    def get_user_id_email(self, email: str) -> str | None:
        """
        Gets the user ID by email.

        Args:
            email (str): The email of the user.
        """
        return next(
            (
                user["id"]
                for user in self._get_users()
                if cast(SlackProfile, user["profile"]).get("email") == email
            ),
            None,
        )

    def _get_users(self) -> Iterator[dict[str, Any]]:
        """
        Lazy function that gets a list of all users in the workspace.

        Args:
            exclude_bots (bool): Whether to exclude bots. Default is True.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.list
        """
        result = self.users_list(limit=300)
        yield from result["members"]
        while next_c := cast(str | None, result["response_metadata"]["next_cursor"]):
            result = self.users_list(cursor=next_c, limit=300)
            yield from result["members"]

    def fetch_members(self, exclude_bots: bool = True) -> list[dict[str, str]]:
        """
        Gets a list of all users in the workspace.

        Args:
            exclude_bots (bool): Whether to exclude bots. Default is True.

        > Check the official documentation of the Slack API for more information: https://api.slack.com/methods/users.list
        """
        return [
            user
            for user in self._get_users()
            if not user["deleted"]
            and not (exclude_bots and (user["is_bot"] or user["id"] == "USLACKBOT"))
        ]

    def open_modal(self, trigger_id: str, view: dict[str, Any]) -> SlackResponse:
        """
        Opens a modal in Slack.

        Args:
            trigger_id (str): The trigger ID.
            view (dict): The view to open.

        Returns:
            dict: The response from the Slack API.
        """
        result = self.views_open(
            trigger_id=trigger_id,
            view=view,
        )

        return SlackResponse.from_sdk(result)

    def update_modal(self, view_id: str, view: dict[str, Any]) -> SlackResponse:
        """
        Updates a modal in Slack.

        Args:
            view_id (str): The view ID.
            view (dict): The view to update.

        Returns:
            dict: The response from the Slack API.
        """
        result = self.views_update(
            view_id=view_id,
            view=view,
        )
        return SlackResponse.from_sdk(result)
