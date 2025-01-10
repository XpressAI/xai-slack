
<p align="center">
  <a href="https://github.com/XpressAI/xircuits/tree/master/xai_components#xircuits-component-library-list">Component Libraries</a> •
  <a href="https://github.com/XpressAI/xircuits/tree/master/project-templates#xircuits-project-templates-list">Project Templates</a>
  <br>
  <a href="https://xircuits.io/">Docs</a> •
  <a href="https://xircuits.io/docs/Installation">Install</a> •
  <a href="https://xircuits.io/docs/category/tutorials">Tutorials</a> •
  <a href="https://xircuits.io/docs/category/developer-guide">Developer Guides</a> •
  <a href="https://github.com/XpressAI/xircuits/blob/master/CONTRIBUTING.md">Contribute</a> •
  <a href="https://www.xpress.ai/blog/">Blog</a> •
  <a href="https://discord.com/invite/vgEg2ZtxCw">Discord</a>
</p>

<p align="center">
<img src=https://user-images.githubusercontent.com/20488299/236126647-9caa4032-80a9-4fe4-98c6-593250a8c0a4.png
" width="450"/>
</p>



<p align="center"><i>Xircuits Component Library to interface with Slack! Create Slack Bots in seconds.</i></p>




---
## Xircuits Component Library for Slack

This library provides a simple way to create and manage custom Slack components bots in your workspace. In this README, you'll find the steps to set up a Slack application and start using the xai-slack library.


## Table of Contents

- [Preview](#preview)
- [Prerequisites](#prerequisites)
- [Main Xircuits Components](#main-xircuits-components)
- [Try the Examples](#try-the-examples)
- [Installation](#installation)

## Preview

### Image Prediction Example

![image_prediction](https://github.com/user-attachments/assets/528d4197-e50a-4a54-b47b-ba4e74c2327f)

### Image Prediction Result

![image_prediction_result](https://github.com/user-attachments/assets/f218f435-48f3-4414-9065-9ec8bad9678c)

### MSG Trigger Example 

![msg_trigger](https://github.com/user-attachments/assets/d5053167-d07a-431e-a9db-d6f77d0de8b0)

### MSG Trigger Result

<img src="https://github.com/user-attachments/assets/2533c74c-b468-4e94-b693-0300d7d5acbe" alt="msg_trigger_result" width="500" height="300" />

### Slack OpenAI Example

![slack_openai](https://github.com/user-attachments/assets/e5791634-7c8e-4a8c-8a29-eb7d709a257d)

### Slack OpenAI Result

![slack_openai_result](https://github.com/user-attachments/assets/3d42ac46-9493-4e99-9d0a-ce57928c4271)

## Prerequisites

Before you begin, you will need the following:

1. A Slack workspace.
2. Python3.9+.
3. Xircuits.

## Main Xircuits Components

### SlackClient Component:

Initializes a Slack WebClient using a provided bot token or environment variable. The created client is added to the context for further use by other components.

<img src="https://github.com/user-attachments/assets/fd80ef48-48f3-4a45-a029-b753e023c30b" alt="SlackClient" width="200" height="75" />

### SlackImageMessageListener Component:

Monitors Slack messages for image attachments and triggers a specified component when such a message is detected. Downloads and processes the attached image.

<img src="https://github.com/user-attachments/assets/43282fe6-20f9-4792-9f53-99b670a5ebbb" alt="SlackImageMessageListener" width="200" height="150" />

### SlackApp Component:

Creates a Slack Bolt `App` instance for managing Slack events and interactions. The app is added to the context for other components to utilize.

### SlackDeployBot Component:

Starts a Socket Mode connection for the Slack app. Can run the connection on a separate thread if required.

### SlackMessageListener Component:

Listens for Slack messages or app mentions and triggers a specified event-handling component. Supports filtering based on app mentions.

### RespondToTrigger Component:

Sends a predefined response to messages containing a specified trigger text. Can reply in threads if enabled.

### RespondToTriggerWithImages Component:

Replies with multiple images to a message containing a specified trigger. Supports optional titles for the images.

### RetrieveQueryImage Component:

Extracts an image from a Slack thread based on a file name mentioned in curly braces and applies a mask (e.g., top, bottom, left, right) if specified.

### ThreadTriggers Component:

Detects specific triggers in Slack messages or replies and executes corresponding branches. Optionally filters mentions, tags, and triggers from the text.

### SlackSendMessageToServerAndChannel Component:

Sends a message to a specific server and channel in Slack.

## Try the Examples

We have provided several example workflows to help you get started with the xai-slack component library. Give them a try and see how you can create custom Slack components for your workspace.

### Message Listener

Check out the `msg_trigger.xircuits` workflow. This example listens for keywords in conversations and responds when a trigger message is detected.

### Image Classifier

Explore the `image_prediction.xircuits` workflow. In this example, the bot watches for attached images in conversations and responds with the predicted class when a trigger message is detected.

Additional Example Requirement: 
```
pip install  torch==2.4.1 torchvision==0.19.1
```

### OpenAI Image Generation

Take a look at the `slack_openai.xircuits` workflow. This example leverages components from the [OpenAI Component Library](https://github.com/XpressAI/xai-openai). The bot enables each Slack thread to have unique and contextual image creation and editing using the OpenAI models.

These examples are designed to help you understand how to use the xai-slack component library effectively in your Slack workspace. Enjoy creating and customizing your components!



## Installation

To use this component library, ensure that you have an existing [Xircuits setup](https://xircuits.io/docs/main/Installation). You can then install the Slack library using the [component library interface](https://xircuits.io/docs/component-library/installation#installation-using-the-xircuits-library-interface), or through the CLI using:

```
xircuits install slack
```

You can also do it manually by cloning and installing it.

```
# base Xircuits directory
git clone https://github.com/XpressAI/xai-slack xai_components/xai_slack
pip install -r xai_components/xai_slack/requirements.txt
```

## Setting Up a Slack Application

### Create a Slack App

1. Go to the [Slack API](https://api.slack.com/apps) page and click "Create New App."
2. Choose "From scratch" and provide a name for your app (e.g., "Xai-Slack Bot").
3. Select the workspace where you want the app to be developed.
4. Click "Create App."

### Set up Your App 

1. Navigate to the **OAuth & Permissions** on the left sidebar and scroll down to the Bot Token Scopes section. Click *Add an OAuth Scope*.
2. add the following scopes to your app:
   - `app_mentions:read` (To read app mentions)
   - `channels:history` (To read messages in public channels)
   - `groups:history` (To read messages in private groups)
   - `files:read` (To read file information)
   - `chat:write` (To send messages in channels)
   -  *Note: this scopes are to enable all the components. For selective components usage  you can check the required scopes and events subscriptions stated each component documentation.*
  
3. Scroll up to the top of the **OAuth & Permissions** page and click *Install App to Workspace*. You’ll be led through Slack’s OAuth UI, where you should allow your app to be installed to your development workspace.
4. Once you authorize the installation, you’ll land on the **OAuth & Permissions** page and see a **Bot User OAuth Access Token** save the generated `xoxb-` token to be used as `SLACK_BOT_TOKEN` later.
5. Then head over to **Basic Information** and scroll down under the App Token section and click **Generate Token and Scopes** to generate an app-level token. Add the `connections:write` scope to this token and save the generated `xapp` token to be used as `SLACK_APP_TOKEN` later.
6. Navigate to **Socket Mode** on the left side menu and toggle to enable.  
7. In your Slack app settings, navigate to "Event Subscriptions" on the left side menu and toggle to enable, scroll down and click *Subscribe to bot events*.
8. subscribe your app to the following events:
   - `app_mention`
   - `file_shared`
   - `message.channels`
   - `message.im`
   - *Note: this Subscriptions are to enable all the components. For selective components usage you can check the required scopes and events subscriptions stated each component documentation.*
9. Create a `.env` file and add both `SLACK_APP_TOKEN` and `SLACK_BOT_TOKEN`, or you can provide these values directly to the components later on.


### Invite the Bot to a Channel

1. Log in to your Slack workspace using the web, desktop, or mobile app.
2. Invite the bot to a channel by sending /invite @YourBotName (replace "YourBotName" with the actual name of your bot) as a message in the channel.



---

Now that your Slack app is set up and configured, you can begin using the xai-slack component library to build custom components for your workspace. Please follow the documentation and examples provided in the library to learn how to create, customize, and manage Slack components using xai-slack.
