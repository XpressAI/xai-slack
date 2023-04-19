# Xai-Slack Component Library

Welcome to the xai-slack component library for building Slack components! This library provides a simple way to create and manage custom Slack components in your workspace. In this README, you'll find the steps to set up a Slack application and start using the xai-slack library.

## Table of Contents

- [Xai-Slack Component Library](#xai-slack-component-library)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setting Up a Slack Application](#setting-up-a-slack-application)
    - [Create a Slack App](#create-a-slack-app)
    - [Configure Ngrok](#configure-ngrok)
    - [Set up Event Subscriptions](#set-up-event-subscriptions)
    - [Subscribe to Bot Events](#subscribe-to-bot-events)
    - [Configure OAuth \& Permissions](#configure-oauth--permissions)
    - [Invite the Bot to a Channel](#invite-the-bot-to-a-channel)
  - [Installation](#installation)
  - [Getting Started with Xai-Slack](#getting-started-with-xai-slack)
    - [Try the Example: msg\_trigger.xircuits](#try-the-example-msg_triggerxircuits)

## Prerequisites

Before you begin, you will need the following:

1. A Slack workspace.
2. [Ngrok](https://ngrok.com/) installed and configured for your development environment.
3. Python3.8+.
4. Xircuits. 

## Setting Up a Slack Application

### Create a Slack App

1. Go to the [Slack API](https://api.slack.com/apps) page and click "Create New App."
2. Choose "From scratch" and provide a name for your app (e.g., "Xai-Slack Bot").
3. Select the workspace where you want the app to be developed.
4. Click "Create App."

### Configure Ngrok

1. Run Ngrok in your development environment using the command: `ngrok http 3000`, port `3000` is where your events listener later on should be running. 
2. Copy the forwarding URL provided by Ngrok (e.g., `https://12345abcde.ngrok.io`). This will be used as your base address. 

### Set up Event Subscriptions

1. In your Slack app settings, navigate to "Event Subscriptions" in the left sidebar.
2. Toggle the "Enable Events" switch on.
3. Enter your Ngrok base address with "/slack/events" attached as the "Request URL" (e.g., `https://12345abcde.ngrok.io/slack/events`).
4. You should see a "Verified" message at the top of the page.

### Subscribe to Bot Events

1. In the "Event Subscriptions" page, scroll down to "Subscribe to bot events."
2. Click "Add Bot User Event" and select the events your bot requires, depending on its tasks. For example:
    - `app_mention` to receive notifications when the bot is mentioned.
    - `message.channels` to receive messages sent in public channels.
    - `message.im` to receive direct messages.
3. Save your changes.

### Configure OAuth & Permissions

1. In your Slack app settings, go to the "OAuth & Permissions" tab.
2. Under "Redirect URLs," add your base URL with "/auth/slack/callback" attached (e.g., `https://12345abcde.ngrok.io/auth/slack/callback`).
3. Scroll down to "OAuth Tokens for Your Workspace" and click "Install to Workspace." Authorize your app.
4. After authorization, you'll be presented with your app's tokens. Copy the "Bot User OAuth Token" (this will be your `SLACK_BOT_TOKEN`).
5. Go back to your app's "Basic Information" page and copy the "Signing Secret" (this will be your `SLACK_SIGNING_SECRET`).
6. Create a `.env` file and add both `SLACK_SIGNING_SECRET` and `SLACK_BOT_TOKEN`, or you can provide these values directly to the components later on.

### Invite the Bot to a Channel

1. Log in to your Slack workspace using the web, desktop, or mobile app.
2. Invite the bot to a channel by sending `/invite @YourBotName` (replace "YourBotName" with the actual name of your bot) as a message in the channel.

## Installation

```
pip install -r requirements.txt
```

## Getting Started with Xai-Slack

Now that your Slack app is set up and configured, you can begin using the xai-slack component library to build custom components for your workspace. Please follow the documentation and examples provided in the library to learn how to create, customize, and manage Slack components using xai-slack.

### Try the Example: msg_trigger.xircuits

We have provided an example component called `msg_trigger.xircuits` that watches for keywords in conversations and responds when a trigger message is detected. Give it a try to see how the xai-slack component library can be used to create custom Slack components for your workspace.
