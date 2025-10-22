# AgenticBilling.AI Usage Data Submission & Reporting Tool

A comprehensive Python script for submitting usage data to and viewing reports from the AgenticBilling.AI platform using CloudEvents-compliant format.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Your API Key](#getting-your-api-key)
- [Installation](#installation)
- [Running the Script](#running-the-script)
- [Features](#features)
- [Example Workflows](#example-workflows)
- [Troubleshooting](#troubleshooting)
- [Security Best Practices](#security-best-practices)

## Prerequisites

- **Python 3.7 or higher** installed on your system
- **Network access** to the AgenticBilling.AI API endpoint
- **API Key** for authentication (see below)

**No additional libraries required** - the script uses only Python standard libraries.

## Getting Your API Key

### Option 1: Use a Pre-Created API Key

If you've already been provided with an API key:
1. Keep it secure - treat it like a password
2. Have it ready to paste when running the script
3. The script will mask it for security (showing only the last 4 characters)

### Option 2: Create a New API Key

1. Log in to the AgenticBilling.AI platform at **https://app.agenticbilling.ai**
2. Navigate to **Settings** → **API Keys**
3. Click **Create New API Key**
4. Give it a descriptive name (e.g., "Usage Submission Script")
5. Copy the generated key immediately - **you won't be able to see it again**
6. Store it securely (e.g., in a password manager)

> **Note:** Each user should have their own API key. Never share keys between users.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/agenticbillingai-api.git
cd agenticbillingai-api
```

2. The script uses only Python standard library modules, so no additional installation is needed.

## Running the Script

### Basic Usage (Interactive Mode)

```bash
python agentic_billing_usage_script.py
```

The script will prompt you for:
1. **Base URL** (defaults to `https://api.agenticbilling.ai`)
2. **API Key** - Paste your API key 

### Advanced Usage (Command Line Arguments)

Skip prompts by providing parameters on the command line:

```bash
python agentic_billing_usage_script.py --base-url https://api.agenticbilling.ai --api-key YOUR_API_KEY_HERE
```

**Available Arguments:**
- `--base-url` - API endpoint URL (default: https://api.agenticbilling.ai)
- `--api-key` - Your API authentication key
- `--provider` - Provider name (default: AgenticBilling.AI)

## Features

### 📤 Send Usage Data

Submit usage events to the AgenticBilling.AI platform with pre-built templates:

1. **Basic Compute Usage** - Virtual machine runtime, compute hours
2. **AI Chat Completion Usage** - LLM tokens, chat requests
3. **Storage Usage** - Storage capacity, operations
4. **SaaS API Usage** - API requests, data transfer
5. **SaaS Batch Processing** - Batch jobs, credits
6. **Custom Usage Event** - Create your own event with custom meters

**Each template allows you to:**
- Preview the event before sending
- Edit any field values (service, quantities, tenant ID, etc.)
- Cancel if needed

### 📊 View Usage & Cost Data

Query and analyze your usage and cost data with comprehensive reporting:

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

## Example Workflows

### Workflow 1: Submit Test Usage Data

1. Run the script: `python agentic_billing_usage_script.py`
2. Enter your API key when prompted
3. Select **1** (Send Usage Data)
4. Select **2** (AI Chat Completion Usage)
5. Review the preview
6. Type **e** to edit values like tenant ID, quantities, or service name
7. Type **s** to send
8. View the confirmation response

### Workflow 2: Review Monthly Costs by Tenant

1. Run the script
2. Enter your API key
3. Select **2** (View Usage & Cost Data)
4. Select **5** (Monthly Cost Summary)
5. Enter date range (or press Enter for last 3 months)
6. Review the breakdown showing:
   - Each month's total cost
   - List of tenants with their individual costs
   - Grand total across all months
7. Export to CSV if needed for further analysis

### Workflow 3: Analyze Service Costs

1. Run the script
2. Select **View Usage & Cost Data**
3. Select **6** (Monthly Cost by Service)
4. Enter date range
5. Review which services are costing the most
6. See percentage breakdown per service
7. Export data for executive reporting

### Workflow 4: Track Daily Usage Trends

1. Run the script
2. Select **View Usage & Cost Data**
3. Select **2** (Daily Usage - Date Range)
4. Enter a week or month date range
5. See daily trends and top services
6. Export to CSV
7. Open in Excel to create charts and visualizations

## Editing Events Before Sending

When submitting usage data, you can edit events before sending:

### Quick Edit Mode
- Quickly update common fields like service, tenant ID, user ID
- Edit meter quantities
- Streamlined interface for fast changes

### Full Edit Mode
- Navigate through entire event structure
- Edit any field including nested objects and arrays
- View full JSON representation
- Make multiple changes before sending

### Edit Options
After previewing an event:
- **(s)end** - Send the event as-is
- **(e)dit** - Edit values before sending
- **(c)ancel** - Cancel and return to main menu

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

### Authentication Issues

**"Invalid API Key" or "401 Unauthorized"**
- Verify your API key is correct (check for copy/paste errors)
- Ensure there are no extra spaces when pasting
- Check that the key hasn't been revoked or expired
- Confirm you're using the correct base URL
- Try creating a new API key

### Connection Issues

**"Connection Error" or "URL Error"**
- Check your internet connection
- Verify the base URL is correct (`https://api.agenticbilling.ai`)
- Ensure your firewall allows outbound HTTPS connections
- Check if a corporate proxy is required
- Try accessing the API URL in a web browser

### Data Issues

**"No Data Found" When Viewing Reports**
- Verify the date range includes periods with usage data
- Check that data has been successfully submitted first
- Ensure you're querying the correct tenant/provider
- Try expanding the date range

**"Unexpected data format" Errors**
- Report this to support with the error details
- The API response format may have changed

### Installation/Runtime Issues

**"Python not found" or "Command not found"**
- Verify Python is installed: `python --version` or `python3 --version`
- Try `python3` instead of `python` on Mac/Linux
- Install Python from https://www.python.org/downloads/

**Script won't start**
- Ensure you're in the correct directory
- Check file permissions: `chmod +x agentic_billing_usage_script.py` (Mac/Linux)
- Try: `python -u agentic_billing_usage_script.py` to disable buffering

## Event Structure Reference

All events follow the **CloudEvents v1.0** specification:

```json
{
  "id": "01JKQ...",
  "specversion": "1.0",
  "type": "ai.agenticbilling.usage.v1",
  "source": "AgenticBilling.AI/usage",
  "time": "2025-01-17T10:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "id": "usage-001",
    "service": "ai.chat",
    "operation": "chat.completion",
    "resourceId": "/ai/models/gpt-4",
    "usageStart": "2025-01-17T09:30:00Z",
    "usageEnd": "2025-01-17T10:30:00Z",
    "meters": [
      {
        "meterId": "chat.input_tokens",
        "quantity": 1500,
        "unit": "tokens"
      }
    ],
    "dimensions": {
      "model": "gpt-4",
      "region": "eastus"
    },
    "tags": {
      "project": "customer-support"
    },
    "tenantId": "org/acme",
    "userId": "user:123"
  }
}
```

## Integration Examples

### Windows Batch File

```batch
@echo off
python agentic_billing_usage_script.py ^
  --base-url https://api.agenticbilling.ai ^
  --api-key %AGENTIC_API_KEY%
```

### Bash Script (Linux/Mac)

```bash
#!/bin/bash
python3 agentic_billing_usage_script.py \
  --base-url https://api.agenticbilling.ai \
  --api-key "$AGENTIC_API_KEY"
```

### PowerShell

```powershell
$env:AGENTIC_API_KEY = "your-api-key-here"
python agentic_billing_usage_script.py `
  --base-url https://api.agenticbilling.ai `
  --api-key $env:AGENTIC_API_KEY
```

© 2025 AgenticBilling.AI - All Rights Reserved
