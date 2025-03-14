class JiraIntegrationTool:
    def __init__(self, jira_url, jira_username, jira_password):
        self.jira_url = jira_url
        self.jira_username = jira_username
        self.jira_password = jira_password
        self.jira = JIRA(jira_url, basic_auth=(jira_username, jira_password))

    def get_issue(self, issue_id):
        return self.jira.issue(issue_id)

    def create_issue(self, project, summary, description):
        issue = self.jira.create_issue(
            project=project,
            summary=summary,
            description=description,
            issuetype={"name": "Task"},
        )
        return issue