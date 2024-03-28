import os
import ssl
import re
import requests
import threading
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from xai_components.base import InArg, OutArg, InCompArg, BaseComponent, Component, xai_component, secret


@xai_component
class SlackClient(Component):
    """
    A component that initializes a Slack WebClient with the provided `slack_bot_token`. The created client is then added to the context for further use by other components.

    ## Inputs
    - `slack_bot_token` (optional): The Slack bot token used to authenticate the WebClient. If not provided, it will try to read the token from the environment variable `SLACK_BOT_TOKEN`.

    ## Outputs
    - Adds the `slack_client` object to the context for other components to use.
    """
    slack_bot_token: InArg[secret]

    def execute(self, ctx) -> None:
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN") if self.slack_bot_token.value is None else self.slack_bot_token.value        
        slack_client = WebClient(slack_bot_token)        
        ctx.update({'slack_client':slack_client})


@xai_component
class SlackApp(Component):
    """
    A component that creates a `slack_bolt.App` instance and adds it to the context.

    ## Inputs
    - `slack_bot_token`: The Slack bot token used to authenticate the app.

    ## Outputs
    - Adds the `app` object to the context for other components to use.

    """
    slack_bot_token:InArg[secret]

    def execute(self, ctx) -> None:
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN") if self.slack_bot_token.value is None else self.slack_bot_token.value
        app = App(token=slack_bot_token)
        ctx.update({'app': app})


@xai_component
class SlackDeployBot(Component):
    """
    A component that initiates a Slack Socket Mode connection using the `SocketModeHandler`.

    ## Inputs
    - `slack_app_token`: The Slack app token used to authenticate the connection.
    - `thread` (optional, default=False): A boolean flag to determine if the connection should run on a separate thread.

    ## Requirements
    - `app` instance in the context (created by `SlackApp` component).
    """
    slack_app_token: InArg[secret]
    thread: InArg[bool]

    def __init__(self):
        super().__init__()
        self.thread.value = False

    def execute(self, ctx) -> None:
        app = ctx['app']
        app_token = os.getenv("SLACK_APP_TOKEN") if self.slack_app_token.value is None else self.slack_app_token.value

        def start_socket_mode():
            SocketModeHandler(app, app_token).start()

        if not self.thread.value:
            start_socket_mode()
        else:
            slack_thread = threading.Thread(target=start_socket_mode)
            slack_thread.start()


@xai_component
class SlackMessageListener(Component):
    """
    A component that listens for messages or app mentions in Slack and triggers the specified `on_event` component.

    ## Inputs
    - `mention_only` (optional, default=False): A boolean flag to determine if the listener should respond only to app mentions.
    - `on_event`: A `BaseComponent` to be executed when the specified event type is triggered.

    ## Outputs
    - `event`: The received Slack event.
    - `message`: The text content of the received Slack message.

    ## Requirements
    - `app` instance in the context (created by `SlackApp` component).

    ### Required Slack permissions:
    - `app_mentions`:read (To read app mentions)
    - `channels:history` or `groups:history` (To read messages in public channels or private groups, respectively)

    ### Required Slack Event Subscriptions:
    - `app_mention` (If mention_only is set to True)
    - `message.channels` (If mention_only is set to False and the bot listens in public channels)
    - `message.groups` (If mention_only is set to False and the bot listens in private groups)
    """
    mention_only: InArg[bool]
    on_event: BaseComponent
    event: OutArg[dict]
    message: OutArg[str]

    def __init__(self):
        super().__init__()
        self.mention_only.value = False

    def execute(self, ctx) -> None:
        app = ctx['app']

        event_type = 'app_mention' if self.mention_only.value else 'message'

        @app.event(event_type)
        def event_listener(event,ack):
            ack()
            self.event.value = event
            self.message.value = event.get('text')
            self.on_event.do(ctx)


@xai_component
class SlackImageMessageListener(Component):
    """
    A component that listens for incoming Slack messages with image attachments and triggers the specified `on_event` component when an image message event occurs.

    ## Inputs
    - `slack_bot_token`: The Slack bot token used for authenticating with the Slack API.

    ## Outputs
    - `event`: The received image message event data.
    - `message`: The text content of the received message.
    - `image`: The first image data in bytes.
    - `on_event`: A `BaseComponent` to be executed when an image message event is received.

    ## Requirements
    - `app` instance in the context (created by `SlackApp` component).
    - `requests` library installed in the Python environment.

    ### Required Slack permissions:
    - `app_mentions`:read (To read app mentions)
    - `channels:history` or `groups:history` (To read messages in public channels or private groups, respectively)
    - `files:read` (To read file information)

    ### Required Slack Event Subscriptions:
    - `app_mention` (If mention_only is set to True)
    - `message.channels` (If mention_only is set to False and the bot listens in public channels)
    - `message.groups` (If mention_only is set to False and the bot listens in private groups)
    """
    slack_bot_token: InArg[secret]
    on_event: BaseComponent
    event: OutArg[dict]
    message: OutArg[str]
    image: OutArg[bytes]

    def execute(self, ctx) -> None:
        app = ctx['app']
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN") if self.slack_bot_token.value is None else self.slack_bot_token.value

        @app.event("app_mention")
        def handle_image_message(event,ack):
            ack()
            message = event.get('text')
            attachments = event.get('files', [])
            for attachment in attachments:
                if attachment['mimetype'].startswith('image/'):
                    if 'url_private_download' in attachment:
                        image_url = attachment['url_private_download']
                        headers = {'Authorization': f'Bearer {slack_bot_token}'}
                        response = requests.get(image_url, headers=headers)
                        self.message.value = message
                        self.image.value = response.content
                        self.event.value = event
                        self.on_event.do(ctx)
                        break


@xai_component
class RespondToTrigger(Component):
    """
    A component that replies to a specific trigger message in a Slack conversation.

    ## Inputs
    - `event`: The message event data.
    - `msg_trigger`: The trigger message to watch for in the conversation.
    - `msg_response`: The response message to send when the trigger message is detected.
    - `in_thread`: (Optional) When set to `True`, the response will be a Slack reply to the message. Default value is `False`.

    ## Requirements
    - `slack_client` instance in the context (created by `SlackClient` component).

    ### Required Slack permissions:
    - `chat:write` (To send messages in channels)
    """
    event:InArg[dict]
    msg_trigger: InArg[str]
    msg_response: InArg[str]
    in_thread:InArg[bool]

    def __init__(self):
        super().__init__()
        self.in_thread.value = False

    def execute(self, ctx) -> None:   
        slack_client = ctx['slack_client']   
        event = self.event.value
        message = event.get('text')
        

        if self.msg_trigger.value in message:
            response = "{}".format(self.msg_response.value)
            thread_ts = event.get('ts') if self.in_thread.value else None
            slack_client.chat_postMessage(channel=event["channel"], text=response,thread_ts=thread_ts)


@xai_component
class RespondtoTriggerWithImages(Component):
    """
    A component that replies with multiple images to a specific trigger message in a Slack conversation.

    ## Inputs
    - `event`: The message event data.
    - `msg_trigger`: The trigger message to watch for in the conversation.
    - `image_urls`: A list of URLs of the images to send as a response.
    - `image_titles`: (Optional) A list of titles for the images. Default value is an empty list.


    ## Outputs
    - `on_reply`: A branch to another component that gets executed when a new reply is made to the parent thread message.
    - `parent_thread_ts`: The timestamp of the parent message to which the first reply was made.

    ## Requirements
    - `slack_client` instance in the context (created by `SlackClient` component).

    ### Required Slack permissions:
    - `chat:write` (To send messages in channels)
    """
    event: InArg[dict]
    msg_trigger: InArg[str]
    image_urls: InArg[list]
    image_titles: InArg[list]

    def execute(self, ctx) -> None:
        slack_client = ctx['slack_client']
        event = self.event.value

        if 'thread_ts' in event:
            thread_ts = event['thread_ts']
        else:
            thread_ts = event.get('ts')

        if event.get("subtype") is None and self.msg_trigger.value in event.get('text'):
            response_blocks = []

            for i, image_url in enumerate(self.image_urls.value):
                image_title = self.image_titles.value[i] if i < len(self.image_titles.value) else i
                response_blocks.append(
                    {
                        "type": "image",
                        "title": {
                            "type": "plain_text",
                            "text": f"{image_title}_0"
                        },
                        "block_id": f"image{i}",
                        "image_url": image_url,
                        "alt_text": f"{image_title}_0"
                    }
                )

            posting = slack_client.chat_postMessage(channel=event["channel"],text="Image(s) shared", blocks=response_blocks, thread_ts=thread_ts)
            
            if posting['message']['thread_ts'] in ctx:
                ctx[posting['message']['thread_ts']].append(posting.get('message')['blocks'][0])
            else:
                ctx.update({posting['message']['thread_ts']:posting.get('message')['blocks']})



@xai_component
class RetrieveQueryImage(Component):
    """
    A component that retrieves the specific image based on the file name mentioned 
    in the slack message within curly braces **`{file_name}`** from the context list of the available images within
    the thread and applies an optional directional edit mask to the image.

    - Directional edit mask is base on the side mentioned in the same slack message within parentheses **`(mask_side)`**
      available options to apply the query to the image:
        - `top`  
        - `bottom` 
        - `left`
        - `right`
        - if no side/ not available side is mention the mask will be applied on the whole image 

    ## Inputs
    - `event`: A dictionary containing the Slack event data.
    - `message`: The text content of the message.

    ## Outputs
    - `image_name`: A list containing the file name of the retrieved image.
    - `image`: The retrieved image data in bytes.
    - `mask`: The mask applied to the image in bytes.

    ## Requirements
    - `PIL` library installed in the Python environment.
    - `requests` library installed in the Python environment.
    """
    
    event: InArg[dict]
    message:InArg[str]
    image_name:OutArg[list]
    image:OutArg[any]
    mask:OutArg[any]

    def execute(self, ctx) -> None:
        import io
        from PIL import Image, ImageDraw
        
        def create_mask(width, height, side):
            mask = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            mask_draw = ImageDraw.Draw(mask)
            if side == "bottom":
                mask_draw.rectangle([0, 0, width, height//2], fill=(0, 0, 0, 255))
            elif side == "top":
                mask_draw.rectangle([0, height//2, width, height], fill=(0, 0, 0, 255))
            elif side == "right":
                mask_draw.rectangle([0, 0, width//2, height], fill=(0, 0, 0, 255))
            elif side == "left":
                mask_draw.rectangle([width//2, 0, width, height], fill=(0, 0, 0, 255))
            else:
                pass
            return mask
        
        file_name = re.search('\{(.+?)\}',self.event.value.get('text'))
        mask_side = re.search('\((.+?)\)',self.event.value.get('text'))
        
        if file_name:
            file_name = file_name.group(1)

        if mask_side:
            mask_side = mask_side.group(1)
        else:
            mask_side = "whole"

        image_list = ctx.get(self.event.value['thread_ts'])
        for image_dict in image_list:
            if image_dict.get('alt_text') == file_name:
                self.image_name.value = [file_name]

                image = requests.get(image_dict.get('image_url'))
                image = Image.open(io.BytesIO(image.content))
                image = image.convert("RGBA")
                width, height = image.size

                mask = create_mask(width, height, mask_side)
                
                image_bytes = io.BytesIO()
                mask_bytes = io.BytesIO()

                image.save(image_bytes, format="PNG")
                mask.save(mask_bytes, format="PNG")

                self.image.value = image_bytes.getvalue()
                self.mask.value = mask_bytes.getvalue()
        

@xai_component
class ThreadTriggers(Component):
    """
    A component that detects and filters messages containing specific triggers in the text, and then executes the corresponding branch.

    ## Inputs
    - `event`: A dictionary containing the Slack event data.
    - `msg_trigger`: The trigger string to look for in a message.
    - `reply_trigger`: The trigger string to look for in a message reply.
    - `filter_message`: A boolean indicating whether to filter out the trigger,mention,tags from the message text before passing it to the next component.

    ## Outputs
    - `out_message`: The filtered message text.
    - `on_message`: A `BaseComponent` to be executed when a message with the `msg_trigger` is detected.
    - `on_reply`: A `BaseComponent` to be executed when a reply message with the `reply_trigger` is detected.
    """
    event: InArg[str]
    msg_trigger:InArg[str]
    reply_trigger:InArg[str]
    filter_message:InArg[bool]
    on_message: BaseComponent
    on_reply: BaseComponent
    out_message:OutArg[str]

    def execute(self, ctx) -> None:
        message = self.event.value.get('text')
        
        def filter_prompt(message,trigger):
            if self.filter_message.value:
                message = re.sub('<@.*?>', '', message)
                message = re.sub('{.*?}', '', message)
                message = re.sub('\(.*?\)', '', message)
                filtered_string = message.strip()
                filtered_prompt = filtered_string.replace(trigger, '')
                return filtered_prompt
            else:
                return message 
        
        if self.msg_trigger.value in message:
            self.out_message.value =  filter_prompt(message,self.msg_trigger.value)
            self.on_message.do(ctx)
        
        if  self.reply_trigger.value in message:
            self.out_message.value =  filter_prompt(message,self.reply_trigger.value)
            if 'thread_ts' in self.event.value: 
                self.on_reply.do(ctx)
