import os
import ssl
import threading
from slack_sdk.web import WebClient
from slackeventsapi import SlackEventAdapter

from xai_components.base import InArg, OutArg, InCompArg, BaseComponent, Component, xai_component


@xai_component
class SlackClient(Component):
    """
    A component that creates a `WebClient` instance for communicating with the Slack API and adds it to the context.

    ## Inputs
    - `slack_bot_token`: The Slack bot token used for authenticating with the Slack API.
    - `use_ssl` (optional, default=True): A boolean flag to determine if SSL should be used for the WebClient.

    ## Outputs
    - `slack_client`: The created `WebClient` instance is added to the context.
    """
    slack_bot_token: InArg[str]
    use_ssl:InArg[bool]

    def __init__(self):
        super().__init__()
        self.use_ssl.value = True

    def execute(self, ctx) -> None:
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN") if self.slack_bot_token.value is None else self.slack_bot_token.value
        
        if self.use_ssl.value:
            slack_client = WebClient(slack_bot_token)
        
        else:
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE        
            slack_client = WebClient(slack_bot_token,ssl=ssl_context)

        ctx.update({'slack_client':slack_client})


@xai_component
class SlackEventsAdaptor(Component):
    """
    A component that creates a `SlackEventAdapter` instance and adds it to the context.

    ## Inputs
    - `slack_signing_secret`: The Slack signing secret used to authenticate incoming requests from Slack (Get from Slack application setting page).

    ## Outputs
    - `slack_events_adapter`: The created `SlackEventAdapter` instance is added to the context.

    """
    slack_signing_secret: InArg[str]

    def execute(self, ctx) -> None:
        slack_signing_secret = os.getenv("SLACK_SIGNING_SECRET") if self.slack_signing_secret.value is None else self.slack_signing_secret.value
        slack_events_adapter = SlackEventAdapter(slack_signing_secret, "/slack/events")
        ctx.update({'slack_events_adapter':slack_events_adapter})


@xai_component
class SlackDeployBot(Component):
    """
    A component that initiates a Slack event listener using the `SlackEventsAdaptor`.

    ## Inputs
    - `port`: The localhost port on which the application will run.
    - `thread` (optional, default=False): A boolean flag to determine if the listener should run on a separate thread.

    ## Requirements
    - `SlackEventsAdaptor`

    """
    port:InCompArg[int]
    thread:InArg[bool]

    def __init__(self):
        super().__init__()
        self.thread.value = False

    def execute(self, ctx) -> None:
        slack_events_adapter = ctx['slack_events_adapter']
        
        def start_events_api():
            slack_events_adapter.start(port=self.port.value)

        if not self.thread.value:
            start_events_api()
        else:
            slack_thread = threading.Thread(target=start_events_api)
            slack_thread.start()


@xai_component
class SlackMessageListener(Component):
    """
    A component that listens for incoming Slack messages using the `slack_events_adapter` and triggers the `on_event` branch when a message event occurs.

    ## Outputs
    - `on_event`: A branch to another component that gets executed when a message event is received.
    - `event`: The received message event data.

    ## Requirements
    - `slack_events_adapter` in the context (created by `SlackEventsAdaptor` component).

    """
    on_event: BaseComponent
    event: OutArg[dict]

    def execute(self, ctx) -> None:
        slack_events_adapter = ctx['slack_events_adapter']

        @slack_events_adapter.on("message")
        def handle_message(event_data):
            self.event.value = event_data
            self.on_event.do(ctx)



@xai_component
class RespondToMsgTrigger(Component):
    """
    A component that replies to a specific trigger message in a Slack conversation.

    ## Inputs
    - `event`: The message event data.
    - `msg_trigger`: The trigger message to watch for in the conversation.
    - `msg_response`: The response message to send when the trigger message is detected.
    - `in_thread`: (Optional) When set to `True`, the response will be a Slack reply to the message. Default value is `False`.

    ## Requirements
    - `slack_client` in the context (created by `SlackClient` component).
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
        message = self.event.value["event"]

        if message.get("subtype") is None and self.msg_trigger.value in message.get('text'):
            response = "<@{}> {}".format(message["user"],self.msg_response.value)
            thread_ts = message.get('ts') if self.in_thread.value else None
            slack_client.chat_postMessage(channel=message["channel"], text=response,thread_ts=thread_ts)