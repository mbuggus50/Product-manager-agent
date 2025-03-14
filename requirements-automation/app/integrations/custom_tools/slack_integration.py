class SlackIntegrationTool:
    def __init__(self, slack_token: str):
        self.slack_token = slack_token
        self.slack_client = slack.WebClient(token=self.slack_token)
        self.slack_channel = "#general"

    def send_message(self, message: str):
        self.slack_client.chat_postMessage(channel=self.slack_channel, text=message)