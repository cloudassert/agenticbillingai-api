# AgenticBilling.AI - Usage Data Submission Tool

A Python-based CLI tool for sending CloudEvents-compliant usage data to the AgenticBilling.AI API and viewing usage and cost reports.

## Features

- **Send Usage Data**: Submit various types of usage events to AgenticBilling.AI
  - Basic Compute Usage
  - AI Chat Completion Usage
  - Storage Usage
  - SaaS API Usage
  - SaaS Batch Processing
  - Custom Usage Events

- **View Reports**: Access comprehensive usage and cost data
  - Hourly Usage Reports
  - Daily Usage Reports (Date Range & Grouped)
  - Daily Cost Reports
  - Monthly Cost Summaries
  - Monthly Cost by Service

- **Data Export**: Export reports to CSV or JSON format

- **Interactive Editing**: Modify usage events before submission with an intuitive editor

- **CloudEvents Compliant**: Follows CloudEvents v1.0 specification

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/agenticbillingai-api.git
cd agenticbillingai-api
```

2. The script uses only Python standard library modules, so no additional installation is needed.

## Usage

### Basic Usage

Run the script:
```bash
python agentic_billing_usage_script.py
```

The script will prompt you for:
- Base URL (defaults to `https://api.agenticbilling.ai`)
- API Key (with masked input)
- Provider name (defaults to `AgenticBilling.AI`)

### Command Line Arguments

You can also provide configuration via command-line arguments:

```bash
python agentic_billing_usage_script.py --base-url https://api.agenticbilling.ai --api-key YOUR_API_KEY --provider "YourProvider"
```

**Arguments:**
- `--base-url`: Base URL for the API
- `--api-key`: API Key for authentication
- `--provider`: Provider name

## Features Overview

### 1. Send Usage Data

Choose from pre-built templates or create custom usage events:

- **Basic Compute Usage**: Track VM runtime and compute hours
- **AI Chat Completion Usage**: Monitor AI model usage (tokens, requests)
- **Storage Usage**: Track storage capacity and operations
- **SaaS API Usage**: Monitor API requests and data transfer
- **SaaS Batch Processing**: Track batch job usage credits
- **Custom Usage Event**: Build your own usage event interactively

Each event can be:
- Previewed before sending
- Edited with an interactive editor
- Sent to the API
- Cancelled

### 2. View Usage & Cost Data

Access various reports:

- **Hourly Usage**: View usage for a specific hour
- **Daily Usage (Date Range)**: See detailed daily usage across date ranges
- **Daily Usage Summary (Grouped)**: Aggregated usage data grouped by day, provider, service, meter, and unit
- **Daily Cost Report**: View costs broken down by day
- **Monthly Cost Summary**: See monthly cost totals
- **Monthly Cost by Service**: View monthly costs broken down by service

All reports support:
- CSV export
- JSON export
- Customizable date ranges
- Optional filtering

### 3. Data Export

Export any report data to:
- **CSV format**: For spreadsheet analysis
- **JSON format**: For programmatic processing

## Usage Event Structure

All usage events follow the CloudEvents v1.0 specification with the following structure:

```json
{
  "id": "01JKQXXXXXXXXXXXXXXXXXXX",
  "specversion": "1.0",
  "type": "ai.agenticbilling.usage.v1",
  "source": "AgenticBilling.AI/usage",
  "time": "2025-10-21T10:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "id": "usage-XXXXXXXXXX",
    "service": "ai.chat",
    "operation": "chat.completion",
    "resourceId": "/ai/models/gpt-4",
    "usageStart": "2025-10-21T10:29:50Z",
    "usageEnd": "2025-10-21T10:30:00Z",
    "meters": [
      {
        "meterId": "chat.input_tokens",
        "quantity": 1500,
        "unit": "tokens"
      }
    ],
    "dimensions": {
      "model": "gpt-4",
      "temperature": "0.7"
    },
    "tags": {
      "project": "customer-support-bot",
      "environment": "production"
    },
    "tenantId": "org/acme",
    "userId": "user:42",
    "projectId": "project/alpha"
  }
}
```
## Examples

### Example 1: Send AI Chat Usage

```bash
python agentic_billing_usage_script.py
# Select "1. Send Usage Data"
# Select "2. AI Chat Completion Usage"
# Review the event
# Type 's' to send or 'e' to edit
```

### Example 2: View Monthly Costs

```bash
python agentic_billing_usage_script.py
# Select "2. View Usage & Cost Data"
# Select "5. View Monthly Cost Summary"
# Enter date range (e.g., "3" for 3 months ago)
# Export to CSV if desired
```

### Example 3: Custom Usage Event

```bash
python agentic_billing_usage_script.py
# Select "1. Send Usage Data"
# Select "6. Custom Usage Event"
# Follow interactive prompts to build your event
```

## Data Fields

### Required Fields
- `id`: Unique event identifier (auto-generated)
- `service`: Service name (e.g., "ai.chat", "compute", "storage")
- `operation`: Operation type (e.g., "chat.completion", "vm.runtime")
- `resourceId`: Resource identifier
- `usageStart`: Usage start timestamp (ISO 8601)
- `usageEnd`: Usage end timestamp (ISO 8601)
- `meters`: Array of meter readings (at least one required)
  - `meterId`: Meter identifier
  - `quantity`: Numeric quantity
  - `unit`: Unit of measurement

### Optional Fields
- `dimensions`: Key-value pairs for additional categorization
- `tags`: Key-value pairs for custom metadata
- `tenantId`: Tenant identifier
- `userId`: User identifier
- `projectId`: Project identifier

## Troubleshooting

### API Key Issues
- Ensure your API key is valid and has proper permissions
- Check that the API key is correctly copied (no extra spaces)

### Connection Issues
- Verify the base URL is correct
- Check your internet connection
- Ensure the API endpoint is accessible

### Date Format Issues
- Use ISO 8601 format: `YYYY-MM-DD` or `YYYY-MM-DD HH:MM:SS`
- Or use relative dates: number of hours/days/months ago

## License

MIT License

Copyright (c) 2025 CLOUD ASSERT LLC

See [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or contributions, please visit the project repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
