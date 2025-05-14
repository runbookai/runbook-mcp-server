I'd like to generate a weekly snippet of my work done this week.

List all Jira issues that match the following conditions:

- Completed by {env[jira][user]} .
- Completed between this Monday and today.

The weekly snippet needs to be concise and highlight recent changes made.

The weekly snippet consists of 3-5 line items. Here is an example:

- did X
- did Y
- did Z

Once the snippet is generated, ask me to review. If this looks good to me,
send the weekly snippet to Slack channel {env[slack][weeklySnippet]}.
