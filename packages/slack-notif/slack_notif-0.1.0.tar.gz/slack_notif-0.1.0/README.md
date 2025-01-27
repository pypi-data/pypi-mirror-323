# slack-notif

A simple Python package to send well-structured Slack notifications for your scripts, including success/error status, execution time, and custom content.

## Installation

```bash
pip install slack-notif
```

## Usage

First, you'll need a Slack bot token. Create one at https://api.slack.com/apps.

### Basic Usage

```python
from slack_notif import NotificationManager

# Initialize the notification manager
notif = NotificationManager(
    token="xoxb-your-token",
    channel="#your-channel"
)

# Use as a decorator
@notif.notify
def my_function():
    # Your code here
    pass

# Add extra content to notifications
@notif.notify(extra_content={"Environment": "Production", "Version": "1.0.0"})
def another_function():
    # Your code here
    pass

# Or send notifications manually
notif.send_notification(
    status="success",
    message="Data processing complete",
    duration=42.5,  # seconds
    extra_content={"Rows Processed": 1000}
)
```

### Features

- ✨ Clean, modern Slack message formatting
- ⏱️ Automatic execution time tracking
- 🎯 Success/error status with appropriate colors
- 📝 Support for custom additional content
- 🔄 Easy-to-use decorator syntax
- ⚡ Simple manual notification sending

### Example Output

The notifications will include:
- A header with the script status (Success/Error)
- The main message
- Execution duration (if provided)
- Any extra content in a clean key-value format

## Development

To set up for development:

```bash
pip install -e ".[dev]"
```

## License

Not affiliated with Slack.

MIT 