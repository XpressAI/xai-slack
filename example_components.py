import os
from slack_sdk import WebClient
import ssl

from xai_components.base import InArg, OutArg, InCompArg, Component, xai_component

@xai_component
class SlackClient(Component):
    slack_bot_token: InArg[str]
    slack_client:OutArg[any]

    def execute(self, ctx) -> None:
        slack_bot_token = os.getenv("SLACK_BOT_TOKEN") if self.slack_bot_token.value is None else self.slack_bot_token.value
        
        ## TODO remove after settling SSL error
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
                
        slack_client = WebClient(slack_bot_token,
                             ssl=ssl_context)
        self.slack_client.value = slack_client
        self.done = True


@xai_component
class PostMessage(Component):
    slack_client:InCompArg[str]
    channel_id: InArg[str]
    message:InArg[str]

    def execute(self, ctx) -> None:
        slack_client = self.slack_client.value
        
        try:
            slack_client.chat_postMessage(
                channel=self.channel_id.value,
                text=self.message.value
            )
            print("Message posted successfully.")
        except Exception as e:
            print(f"Error posting message: {type(e).__name__} - {e}")
            
        self.done = True
        
@xai_component
class PostThread(Component):
    slack_client:InCompArg[str]
    channel_id: InArg[str]
    message:InArg[str]
    thread_ts_in:InArg[str]
    thread_ts_out:OutArg[str]
    

    def execute(self, ctx) -> None:
        slack_client = self.slack_client.value
        thread_ts = self.thread_ts_in.value
        for i in range(3):
            try:
                if not thread_ts:
                    response = slack_client.chat_postMessage(
                        channel=self.channel_id.value,
                        text=self.message.value
                    )
                    thread_ts = response.get('ts')
                    print("First message posted successfully.")
                else:
                    slack_client.chat_postMessage(
                        channel=self.channel_id.value,
                        text=self.message.value,
                        thread_ts=thread_ts
                    )
                    print("Thread reply posted successfully.")
            except Exception as e:
                print(f"Error posting message: {type(e).__name__} - {e}")
            
        self.thread_ts_out.value = thread_ts   
        
        self.done = True