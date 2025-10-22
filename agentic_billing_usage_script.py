"""
AgenticBilling.AI Usage Data Submission Script
Send CloudEvents-compliant usage data to AgenticBilling API
"""

import json
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timedelta, timezone
import random
import string
import argparse
import getpass
import sys
import csv
import os

# --------------------------------
# 🔧 CONFIGURATION
# --------------------------------

def getpass_with_asterisks(prompt="Password: "):
    """Get password input with asterisk feedback"""
    print(prompt, end='', flush=True)

    try:
        # Try Windows method (msvcrt)
        import msvcrt
        password = []
        while True:
            char = msvcrt.getch()
            if char in (b'\r', b'\n'):  # Enter key
                print()  # New line
                break
            elif char == b'\x08':  # Backspace
                if password:
                    password.pop()
                    # Move cursor back, print space, move back again
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif char == b'\x03':  # Ctrl+C
                print()
                raise KeyboardInterrupt
            else:
                # Regular character
                password.append(char.decode('utf-8', errors='ignore'))
                sys.stdout.write('*')
                sys.stdout.flush()
        return ''.join(password)
    except ImportError:
        # Unix/Linux method (termios)
        try:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                password = []
                while True:
                    char = sys.stdin.read(1)
                    if char in ('\r', '\n'):
                        print()
                        break
                    elif char == '\x7f':  # Backspace
                        if password:
                            password.pop()
                            sys.stdout.write('\b \b')
                            sys.stdout.flush()
                    elif char == '\x03':  # Ctrl+C
                        print()
                        raise KeyboardInterrupt
                    else:
                        password.append(char)
                        sys.stdout.write('*')
                        sys.stdout.flush()
                return ''.join(password)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except:
            # Fallback to standard getpass if platform-specific methods fail
            return getpass.getpass(prompt)

# Parse command line arguments
parser = argparse.ArgumentParser(description='Send usage data to AgenticBilling API')
parser.add_argument('--base-url', help='Base URL for the API (e.g., https://api.agenticbilling.ai)')
parser.add_argument('--api-key', help='API Key for authentication')
parser.add_argument('--provider', help='Provider name (default: AgenticBilling.AI)')
args = parser.parse_args()

# Get values from command line or prompt user
if args.base_url:
    BASE_URL = args.base_url
else:
    BASE_URL = input("Enter base URL (or press Enter for https://api.agenticbilling.ai): ").strip()
    if not BASE_URL:
        BASE_URL = "https://api.agenticbilling.ai"
    print(f"✓ Base URL set to: {BASE_URL}")

if args.api_key:
    API_KEY = args.api_key
else:
    print("\n🔑 Enter API Key")
    API_KEY = getpass_with_asterisks("Paste or type here: ").strip()

    if API_KEY:
        masked_key = '*' * max(0, len(API_KEY) - 4) + API_KEY[-4:] if len(API_KEY) > 4 else '*' * len(API_KEY)
        print(f"✓ API Key received ({len(API_KEY)} characters): {masked_key}")
    else:
        print("❌ Warning: No API Key entered!")

PROVIDER = args.provider if args.provider else "AgenticBilling.AI"

# --------------------------------
# 🛠️ HELPER FUNCTIONS
# --------------------------------

def generate_event_id():
    """Generate a CloudEvents compliant ID using ULID-like format"""
    timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
    timestamp_b36 = to_base36(timestamp).upper()
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    event_id = f"01JKQ{timestamp_b36}{random_str}"
    return event_id[:26]

def to_base36(num):
    """Convert number to base36 string"""
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    while num:
        num, remainder = divmod(num, 36)
        result = chars[remainder] + result
    return result or '0'

def get_current_timestamp():
    """Get current ISO timestamp"""
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def get_timestamp_ago(hours=1):
    """Get timestamp N hours ago"""
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat().replace('+00:00', 'Z')

def make_request(url, method="POST", headers=None, body=None, params=None):
    """Make HTTP request to API"""
    if headers is None:
        headers = {}

    # Add API Key to headers
    headers['x-api-key'] = API_KEY

    # Add query parameters
    if params:
        url += "?" + urllib.parse.urlencode(params)

    # Prepare request
    if body:
        body_bytes = json.dumps(body).encode('utf-8')
        headers['Content-Type'] = 'application/json'
        headers['Content-Length'] = str(len(body_bytes))
    else:
        body_bytes = None

    req = urllib.request.Request(url, data=body_bytes, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as res:
            data = res.read().decode('utf-8')
            print(f"\n✅ Success! Status Code: {res.status}")
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTP Error {e.code}: {e.reason}")
        error_body = e.read().decode('utf-8')
        print(f"Error details: {error_body}")
        return None
    except urllib.error.URLError as e:
        print(f"\n❌ URL Error: {e.reason}")
        return None

# --------------------------------
# 📊 USAGE EVENT TEMPLATES
# --------------------------------

def create_basic_compute_usage():
    """Create a basic compute usage event"""
    return {
        "id": generate_event_id(),
        "specversion": "1.0",
        "type": "ai.agenticbilling.usage.v1",
        "source": f"{PROVIDER}/usage",
        "time": get_current_timestamp(),
        "datacontenttype": "application/json",
        "data": {
            "id": f"usage-{generate_event_id()}",
            "service": "compute",
            "operation": "vm.runtime",
            "resourceId": "/subscriptions/abc123/resourceGroups/rg1/providers/Microsoft.Compute/virtualMachines/vm1",
            "usageStart": get_timestamp_ago(1),
            "usageEnd": get_current_timestamp(),
            "meters": [
                {
                    "meterId": "compute.hours",
                    "quantity": 1.0,
                    "unit": "hours"
                }
            ],
            "dimensions": {
                "region": "eastus",
                "vmSize": "Standard_D2s_v3",
                "environment": "production"
            },
            "tags": {
                "team": "engineering",
                "cost-center": "product"
            }
        }
    }

def create_ai_chat_usage():
    """Create an AI chat completion usage event"""
    return {
        "id": generate_event_id(),
        "specversion": "1.0",
        "type": "ai.agenticbilling.usage.v1",
        "source": f"{PROVIDER}/usage",
        "time": get_current_timestamp(),
        "datacontenttype": "application/json",
        "data": {
            "id": f"usage-ai-{generate_event_id()}",
            "service": "ai.chat",
            "operation": "chat.completion",
            "resourceId": "/ai/models/gpt-4",
            "usageStart": (datetime.now(timezone.utc) - timedelta(seconds=10)).isoformat().replace('+00:00', 'Z'),
            "usageEnd": get_current_timestamp(),
            "meters": [
                {
                    "meterId": "chat.input_tokens",
                    "quantity": 1500,
                    "unit": "tokens"
                },
                {
                    "meterId": "chat.output_tokens",
                    "quantity": 750,
                    "unit": "tokens"
                },
                {
                    "meterId": "chat.requests",
                    "quantity": 1,
                    "unit": "requests"
                }
            ],
            "dimensions": {
                "model": "gpt-4",
                "temperature": "0.7",
                "max_tokens": "2000"
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

def create_storage_usage():
    """Create a storage usage event"""
    return {
        "id": generate_event_id(),
        "specversion": "1.0",
        "type": "ai.agenticbilling.usage.v1",
        "source": f"{PROVIDER}/usage",
        "time": get_current_timestamp(),
        "datacontenttype": "application/json",
        "data": {
            "id": f"usage-storage-{generate_event_id()}",
            "service": "storage",
            "operation": "storage.blob.write",
            "resourceId": "/subscriptions/abc123/resourceGroups/rg1/providers/Microsoft.Storage/storageAccounts/sa1",
            "usageStart": get_timestamp_ago(1),
            "usageEnd": get_current_timestamp(),
            "meters": [
                {
                    "meterId": "storage.capacity",
                    "quantity": 100.5,
                    "unit": "GB"
                },
                {
                    "meterId": "storage.operations",
                    "quantity": 1000,
                    "unit": "operations"
                }
            ],
            "dimensions": {
                "region": "westus",
                "tier": "standard",
                "redundancy": "LRS"
            },
            "tags": {
                "department": "data-analytics",
                "cost-center": "engineering"
            },
            "tenantId": "org/contoso",
            "projectId": "project/data-pipeline"
        }
    }

def create_saas_api_usage():
    """Create a SaaS API usage event"""
    return {
        "id": generate_event_id(),
        "specversion": "1.0",
        "type": "ai.agenticbilling.usage.v1",
        "source": f"{PROVIDER}/usage",
        "time": get_current_timestamp(),
        "datacontenttype": "application/json",
        "data": {
            "id": f"usage-api-{generate_event_id()}",
            "service": "api",
            "operation": "api.request",
            "resourceId": "/api/v1/analytics/report",
            "usageStart": (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat().replace('+00:00', 'Z'),
            "usageEnd": get_current_timestamp(),
            "meters": [
                {
                    "meterId": "api.requests",
                    "quantity": 1,
                    "unit": "requests"
                },
                {
                    "meterId": "api.data_transfer",
                    "quantity": 2.5,
                    "unit": "MB"
                }
            ],
            "dimensions": {
                "endpoint": "/api/v1/analytics/report",
                "method": "POST",
                "status_code": "200",
                "client_id": "client-xyz"
            },
            "tags": {
                "api_version": "v1",
                "environment": "production"
            },
            "tenantId": "org/saascompany",
            "userId": "user:123"
        }
    }

def create_saas_batch_processing():
    """Create a SaaS batch processing usage event"""
    return {
        "id": generate_event_id(),
        "specversion": "1.0",
        "type": "ai.agenticbilling.usage.v1",
        "source": f"{PROVIDER}/usage",
        "time": get_current_timestamp(),
        "datacontenttype": "application/json",
        "data": {
            "id": generate_event_id(),
            "resourceId": "saas.ai:user-001",
            "service": "saas.ai",
            "operation": "batch.process",
            "quantity": 2,
            "unit": "credits",
            "usageStart": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat().replace('+00:00', 'Z'),
            "usageEnd": get_current_timestamp(),
            "meters": [
                {
                    "meterId": "saas.ai.primary",
                    "quantity": 3,
                    "unit": "credits"
                },
                {
                    "meterId": "saas.ai.requests",
                    "quantity": 2,
                    "unit": "count"
                }
            ],
            "dimensions": {
                "region": "westus2",
                "tier": "pro"
            },
            "tenantId": "tenant-001",
            "userId": "user-001",
            "tags": {
                "env": "prod",
                "team": "research"
            }
        }
    }

def create_custom_usage():
    """Create a custom usage event with user input"""
    print("\n🔧 Creating Custom Usage Event")

    event = {
        "id": generate_event_id(),
        "specversion": "1.0",
        "type": "ai.agenticbilling.usage.v1",
        "source": f"{PROVIDER}/usage",
        "time": get_current_timestamp(),
        "datacontenttype": "application/json",
        "data": {}
    }

    # Gather data
    event["data"]["id"] = input("Usage ID (press Enter for auto-generated): ").strip() or f"usage-{generate_event_id()}"
    event["data"]["service"] = input("Service name (e.g., 'compute', 'ai.chat'): ").strip()
    event["data"]["operation"] = input("Operation (e.g., 'vm.runtime', 'chat.completion'): ").strip()
    event["data"]["resourceId"] = input("Resource ID: ").strip()

    # Time range
    hours_ago = input("Usage started how many hours ago? (default: 1): ").strip()
    hours_ago = int(hours_ago) if hours_ago else 1
    event["data"]["usageStart"] = get_timestamp_ago(hours_ago)
    event["data"]["usageEnd"] = get_current_timestamp()

    # Meters
    meters = []
    print("\n📊 Add Meters (at least one required)")
    while True:
        meter_id = input(f"  Meter ID #{len(meters)+1} (or press Enter to finish): ").strip()
        if not meter_id:
            if len(meters) == 0:
                print("  ❌ At least one meter is required")
                continue
            break

        quantity = float(input(f"  Quantity for '{meter_id}': ").strip())
        unit = input(f"  Unit for '{meter_id}' (e.g., 'hours', 'tokens', 'GB'): ").strip()

        meters.append({
            "meterId": meter_id,
            "quantity": quantity,
            "unit": unit
        })

    event["data"]["meters"] = meters

    # Optional fields
    add_dimensions = input("\nAdd dimensions? (y/n): ").strip().lower() == 'y'
    if add_dimensions:
        dimensions = {}
        while True:
            key = input("  Dimension key (or press Enter to finish): ").strip()
            if not key:
                break
            value = input(f"  Value for '{key}': ").strip()
            dimensions[key] = value
        if dimensions:
            event["data"]["dimensions"] = dimensions

    add_tags = input("\nAdd tags? (y/n): ").strip().lower() == 'y'
    if add_tags:
        tags = {}
        while True:
            key = input("  Tag key (or press Enter to finish): ").strip()
            if not key:
                break
            value = input(f"  Value for '{key}': ").strip()
            tags[key] = value
        if tags:
            event["data"]["tags"] = tags

    # Optional tenant/user/project IDs
    tenant_id = input("\nTenant ID (optional): ").strip()
    if tenant_id:
        event["data"]["tenantId"] = tenant_id

    user_id = input("User ID (optional): ").strip()
    if user_id:
        event["data"]["userId"] = user_id

    project_id = input("Project ID (optional): ").strip()
    if project_id:
        event["data"]["projectId"] = project_id

    return event

# --------------------------------
# 📝 EDIT EVENT FUNCTION
# --------------------------------

def flatten_dict(d, parent_key='', sep='.'):
    """Flatten nested dictionary to path: value pairs"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.extend(flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                else:
                    items.append((f"{new_key}[{i}]", item))
        else:
            items.append((new_key, v))
    return dict(items)

def set_nested_value(d, path, value):
    """Set value in nested dictionary using path"""
    keys = path.replace(']', '').split('[')
    keys = [k for part in keys for k in part.split('.') if k]

    current = d
    for i, key in enumerate(keys[:-1]):
        if key.isdigit():
            key = int(key)
        if isinstance(current, list):
            current = current[key]
        else:
            if key not in current:
                # Determine if next key is numeric (list) or not (dict)
                next_key = keys[i + 1]
                current[key] = [] if next_key.isdigit() else {}
            current = current[key]

    last_key = keys[-1]
    if last_key.isdigit():
        last_key = int(last_key)

    # Try to preserve type
    if isinstance(current[last_key] if isinstance(current, dict) else current[last_key], (int, float)):
        try:
            value = float(value) if '.' in value else int(value)
        except:
            pass

    if isinstance(current, list):
        current[last_key] = value
    else:
        current[last_key] = value

def edit_event_value(event, path=""):
    """Edit event with improved flat view"""
    while True:
        # Flatten and display all editable fields
        flat = flatten_dict(event)

        print("\n" + "="*70)
        print("📝 EDIT EVENT - All Fields")
        print("="*70)

        # Group by category
        categories = {}
        for path, value in flat.items():
            category = path.split('.')[0] if '.' in path else 'root'
            if category not in categories:
                categories[category] = []
            categories[category].append((path, value))

        # Display grouped fields
        field_num = 1
        path_to_num = {}
        for category, fields in sorted(categories.items()):
            print(f"\n[{category.upper()}]")
            for path, value in fields:
                value_str = str(value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                print(f"  {field_num:2d}. {path:40s} = {value_str}")
                path_to_num[field_num] = path
                field_num += 1

        print("\n" + "="*70)
        print("Options: [number] to edit field | 'quick' for quick edits | 'json' to view full JSON | 'done' to finish")
        choice = input("➤ ").strip().lower()

        if choice == 'done':
            break
        elif choice == 'json':
            print("\n" + "="*70)
            print("FULL JSON")
            print("="*70)
            print(json.dumps(event, indent=2))
            input("\nPress Enter to continue...")
        elif choice == 'quick':
            print("\n🚀 Quick Edit Mode - Common Fields")
            print("="*70)
            print("Leave blank to skip a field")

            # Common fields for quick editing
            quick_fields = [
                ('data.service', 'Service'),
                ('data.operation', 'Operation'),
                ('data.resourceId', 'Resource ID'),
                ('data.tenantId', 'Tenant ID'),
                ('data.userId', 'User ID'),
            ]

            for path, label in quick_fields:
                try:
                    current = get_nested_value(event, path)
                    new_val = input(f"{label} [{current}]: ").strip()
                    if new_val:
                        set_nested_value(event, path, new_val)
                        print(f"  ✓ Updated")
                except:
                    pass

            # Edit meters quantities
            print("\n📊 Edit Meter Quantities")
            flat_meters = {k: v for k, v in flat.items() if 'meters' in k and 'quantity' in k}
            for path, value in flat_meters.items():
                meter_id = path.replace('.quantity', '.meterId')
                meter_name = flat.get(meter_id, 'Unknown')
                new_val = input(f"{meter_name} quantity [{value}]: ").strip()
                if new_val:
                    try:
                        set_nested_value(event, path, float(new_val))
                        print(f"  ✓ Updated")
                    except:
                        print(f"  ✗ Invalid number")

        elif choice.isdigit():
            num = int(choice)
            if num in path_to_num:
                path = path_to_num[num]
                current_value = flat[path]
                print(f"\nEditing: {path}")
                print(f"Current value: {current_value}")
                new_value = input("New value (or press Enter to keep): ").strip()

                if new_value:
                    try:
                        set_nested_value(event, path, new_value)
                        print(f"✅ Updated '{path}' to: {new_value}")
                    except Exception as e:
                        print(f"❌ Error: {e}")
            else:
                print("❌ Invalid field number")
        else:
            print("❌ Invalid choice")

def get_nested_value(d, path):
    """Get value from nested dictionary using path"""
    keys = path.replace(']', '').split('[')
    keys = [k for part in keys for k in part.split('.') if k]

    current = d
    for key in keys:
        if key.isdigit():
            key = int(key)
        current = current[key]
    return current

# --------------------------------
# 📤 SEND USAGE FUNCTION
# --------------------------------

def send_usage_event(event_template_func, template_name):
    """Send a usage event to the API"""
    print(f"\n{'='*60}")
    print(f"📤 Sending: {template_name}")
    print(f"{'='*60}")

    # Generate event
    event = event_template_func()

    was_sent = False
    while True:
        # Display event preview
        print("\n📋 Event Preview:")
        print(json.dumps(event, indent=2))

        action = input("\n➡️  (s)end, (e)dit, or (c)ancel? ").strip().lower()

        if action == 's' or action == 'send':
            # Send request
            url = f"{BASE_URL}/api/v1/cloudevents/usage"
            params = {"provider": PROVIDER}

            result = make_request(url, method="POST", body=event, params=params)

            if result:
                print("\n📘 Response:")
                print(json.dumps(result, indent=2) if isinstance(result, dict) else result)
                was_sent = True
            break

        elif action == 'e' or action == 'edit':
            edit_event_value(event)
            # Loop will continue and show preview again

        elif action == 'c' or action == 'cancel':
            print("⏭️  Cancelled")
            break

        else:
            print("❌ Invalid choice. Please enter 's' (send), 'e' (edit), or 'c' (cancel)")

    return was_sent

# --------------------------------
# 💾 EXPORT FUNCTIONS
# --------------------------------

def export_to_json(data, filename=None):
    """Export data to JSON file"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"usage_data_{timestamp}.json"

    # Ensure .json extension
    if not filename.endswith('.json'):
        filename += '.json'

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"\n✅ Data exported to: {os.path.abspath(filename)}")
        return True
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        return False

def export_to_csv(data, filename=None):
    """Export data to CSV file"""
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"usage_data_{timestamp}.csv"

    # Ensure .csv extension
    if not filename.endswith('.csv'):
        filename += '.csv'

    try:
        # Extract items from paged result
        if isinstance(data, dict):
            items = data.get('items', [data])
            rows = data.get('rows', items)  # For grouped data
        elif isinstance(data, list):
            rows = data
        else:
            rows = [data]

        if not rows:
            print("\n❌ No data to export")
            return False

        # Get all unique keys from all rows
        fieldnames = set()
        for row in rows:
            if isinstance(row, dict):
                fieldnames.update(row.keys())

        fieldnames = sorted(list(fieldnames))

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for row in rows:
                if isinstance(row, dict):
                    # Convert nested objects to strings
                    flat_row = {}
                    for key, value in row.items():
                        if isinstance(value, (dict, list)):
                            flat_row[key] = json.dumps(value)
                        else:
                            flat_row[key] = value
                    writer.writerow(flat_row)

        print(f"\n✅ Data exported to: {os.path.abspath(filename)}")
        return True
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        return False

def prompt_export(data, data_type="data"):
    """Prompt user if they want to export the data"""
    export_choice = input(f"\n💾 Export {data_type}? (y/N): ").strip().lower()

    if export_choice != 'y':
        return

    print("\nExport Format:")
    print("1. CSV (tabular data) [default]")
    print("2. JSON (complete data)")
    format_choice = input("Select format (1-2 or press Enter for CSV): ").strip()

    # Default to CSV if no choice
    if not format_choice:
        format_choice = '1'

    filename = input("Enter filename (or press Enter for auto-generated): ").strip()

    if format_choice == '2':
        export_to_json(data, filename if filename else None)
    elif format_choice == '1':
        export_to_csv(data, filename if filename else None)
    else:
        print("❌ Invalid choice")

# --------------------------------
# 📊 VIEW USAGE & COST DATA
# --------------------------------

def view_usage_data():
    """View usage and cost data from the API"""
    print("\n" + "="*70)
    print("📊 VIEW USAGE & COST DATA")
    print("="*70)

    while True:
        print("\nOptions:")
        print("1. View Hourly Usage")
        print("2. View Daily Usage (Date Range)")
        print("3. View Daily Usage Summary (Grouped)")
        print("4. View Daily Cost Report")
        print("5. View Monthly Cost Summary")
        print("6. View Monthly Cost by Service")
        print("0. Back to Main Menu")

        choice = input("\nSelect option (0-6): ").strip()

        if choice == '0':
            break
        elif choice == '1':
            view_hourly_usage()
        elif choice == '2':
            view_daily_usage()
        elif choice == '3':
            view_daily_usage_grouped()
        elif choice == '4':
            view_daily_cost_report()
        elif choice == '5':
            view_monthly_cost_summary()
        elif choice == '6':
            view_monthly_service_cost_summary()
        else:
            print("❌ Invalid choice")

def view_hourly_usage():
    """View usage for a specific hour"""
    print("\n📅 Hourly Usage")
    print("="*70)

    # Get hour input
    hour_input = input("\nEnter usage hour (YYYY-MM-DD HH:00) or hours ago (default: 1): ").strip()

    if not hour_input or hour_input.isdigit():
        hours_ago = int(hour_input) if hour_input else 1
        usage_hour = datetime.now(timezone.utc) - timedelta(hours=hours_ago)
        # Round to the hour
        usage_hour = usage_hour.replace(minute=0, second=0, microsecond=0)
    else:
        try:
            usage_hour = datetime.fromisoformat(hour_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    url = f"{BASE_URL}/api/v1/reports/usage/hourly"
    params = {
        "usageHour": usage_hour.isoformat().replace('+00:00', 'Z')
    }

    result = make_request(url, method="GET", params=params)

    if result:
        display_paged_usage_data(result, f"Hourly Usage for {usage_hour.strftime('%Y-%m-%d %H:00')}", allow_export=True)
    else:
        print("❌ No data retrieved")

def view_daily_usage():
    """View daily usage for a date range"""
    print("\n📅 Daily Usage (Date Range)")
    print("="*70)

    # Get date range
    from_input = input("\nFrom date (YYYY-MM-DD) or days ago (default: 7): ").strip()

    if not from_input or from_input.isdigit():
        days_ago = int(from_input) if from_input else 7
        from_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            from_date = datetime.fromisoformat(from_input).replace(tzinfo=timezone.utc, hour=0, minute=0, second=0, microsecond=0)
        except:
            print("❌ Invalid date format")
            return

    to_input = input("To date (YYYY-MM-DD) or press Enter for today: ").strip()

    if not to_input:
        to_date = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)
    elif to_input.isdigit():
        days_ago = int(to_input)
        to_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        try:
            to_date = datetime.fromisoformat(to_input).replace(tzinfo=timezone.utc, hour=23, minute=59, second=59, microsecond=999999)
        except:
            print("❌ Invalid date format")
            return

    url = f"{BASE_URL}/api/v1/reports/usage/daily"
    params = {
        "fromDate": from_date.isoformat().replace('+00:00', 'Z'),
        "toDate": to_date.isoformat().replace('+00:00', 'Z')
    }

    result = make_request(url, method="GET", params=params)

    if result:
        display_daily_usage_data(result, from_date, to_date, allow_export=True)
    else:
        print("❌ No data retrieved")

def view_daily_usage_grouped():
    """View daily usage summary grouped by specified fields"""
    print("\n📊 Daily Usage Summary (Grouped)")
    print("="*70)

    # Get date range
    from_input = input("\nFrom date (YYYY-MM-DD) or days ago (default: 7): ").strip()

    if not from_input or from_input.isdigit():
        days_ago = int(from_input) if from_input else 7
        from_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            from_date = datetime.fromisoformat(from_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    to_input = input("To date (YYYY-MM-DD) or press Enter for today: ").strip()

    if not to_input:
        to_date = datetime.now(timezone.utc)
    else:
        try:
            to_date = datetime.fromisoformat(to_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    # Optional filters
    print("\nOptional Filters (press Enter to skip):")
    provider_filter = input("  Provider: ").strip()
    service_filter = input("  Service: ").strip()
    meter_filter = input("  Meter ID: ").strip()

    url = f"{BASE_URL}/api/v1/reports/usage/daily-grouped"
    params = {
        "fromDate": from_date.isoformat().replace('+00:00', 'Z'),
        "toDate": to_date.isoformat().replace('+00:00', 'Z'),
        "groupBy": "UsageDay,Provider,Service,MeterId,Unit",
        "take": 1000
    }

    if provider_filter:
        params["providerCsv"] = provider_filter
    if service_filter:
        params["serviceCsv"] = service_filter
    if meter_filter:
        params["meterIdCsv"] = meter_filter

    result = make_request(url, method="GET", params=params)

    if result:
        display_grouped_data(result, allow_export=True)
    else:
        print("❌ No data retrieved")

def view_daily_cost_report():
    """View daily cost report"""
    print("\n💰 Daily Cost Report")
    print("="*70)

    # Get date range
    from_input = input("\nFrom date (YYYY-MM-DD) or days ago (default: 7): ").strip()

    if not from_input or from_input.isdigit():
        days_ago = int(from_input) if from_input else 7
        from_date = (datetime.now(timezone.utc) - timedelta(days=days_ago)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            from_date = datetime.fromisoformat(from_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    to_input = input("To date (YYYY-MM-DD) or press Enter for today: ").strip()

    if not to_input:
        to_date = datetime.now(timezone.utc)
    else:
        try:
            to_date = datetime.fromisoformat(to_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    url = f"{BASE_URL}/api/v1/reports/priced/daily"
    params = {
        "fromDate": from_date.isoformat().replace('+00:00', 'Z'),
        "toDate": to_date.isoformat().replace('+00:00', 'Z')
    }

    result = make_request(url, method="GET", params=params)

    if result:
        display_daily_cost_data(result, from_date, to_date, allow_export=True)
    else:
        print("❌ No data retrieved")

def view_monthly_cost_summary():
    """View monthly cost summary"""
    print("\n💰 Monthly Cost Summary")
    print("="*70)

    # Get date range
    from_input = input("\nFrom date (YYYY-MM-DD) or months ago (default: 3): ").strip()

    if not from_input or from_input.isdigit():
        months_ago = int(from_input) if from_input else 3
        from_date = (datetime.now(timezone.utc) - timedelta(days=months_ago*30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            from_date = datetime.fromisoformat(from_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    to_input = input("To date (YYYY-MM-DD) or press Enter for today: ").strip()

    if not to_input:
        to_date = datetime.now(timezone.utc)
    else:
        try:
            to_date = datetime.fromisoformat(to_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    url = f"{BASE_URL}/api/v1/reports/priced/monthly/tenantSummary"
    params = {
        "fromDate": from_date.isoformat().replace('+00:00', 'Z'),
        "toDate": to_date.isoformat().replace('+00:00', 'Z')
    }

    result = make_request(url, method="GET", params=params)

    if result:
        display_monthly_summary_data(result, allow_export=True)
    else:
        print("❌ No data retrieved")

def view_monthly_service_cost_summary():
    """View monthly cost summary by service"""
    print("\n💰 Monthly Cost by Service")
    print("="*70)

    # Get date range
    from_input = input("\nFrom date (YYYY-MM-DD) or months ago (default: 3): ").strip()

    if not from_input or from_input.isdigit():
        months_ago = int(from_input) if from_input else 3
        from_date = (datetime.now(timezone.utc) - timedelta(days=months_ago*30)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        try:
            from_date = datetime.fromisoformat(from_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    to_input = input("To date (YYYY-MM-DD) or press Enter for today: ").strip()

    if not to_input:
        to_date = datetime.now(timezone.utc)
    else:
        try:
            to_date = datetime.fromisoformat(to_input).replace(tzinfo=timezone.utc)
        except:
            print("❌ Invalid date format")
            return

    url = f"{BASE_URL}/api/v1/reports/priced/monthly/tenantServiceSummary"
    params = {
        "fromDate": from_date.isoformat().replace('+00:00', 'Z'),
        "toDate": to_date.isoformat().replace('+00:00', 'Z')
    }

    result = make_request(url, method="GET", params=params)

    if result:
        display_monthly_service_summary_data(result, allow_export=True)
    else:
        print("❌ No data retrieved")

def display_paged_usage_data(data, title, allow_export=False):
    """Display paged usage data from API"""
    print(f"\n📊 {title}")
    print("="*70)

    if not isinstance(data, dict):
        print("❌ Unexpected data format")
        print(json.dumps(data, indent=2))
        input("\nPress Enter to continue...")
        return

    items = data.get('items', [])
    total_count = data.get('totalCount', len(items))

    if not items:
        print("\n✓ No usage data found for this period")
        input("\nPress Enter to continue...")
        return

    print(f"\nShowing {len(items)} of {total_count} records")
    print("="*70)

    for idx, item in enumerate(items[:20], 1):  # Limit to 20 for display
        print(f"\n[Record #{idx}]")
        print(f"  Provider:    {item.get('provider', 'N/A')}")
        print(f"  Service:     {item.get('service', 'N/A')}")
        print(f"  Operation:   {item.get('operation', 'N/A')}")
        print(f"  Resource:    {item.get('resourceId', 'N/A')[:50]}")
        print(f"  Meter ID:    {item.get('meterId', 'N/A')}")
        print(f"  Quantity:    {item.get('quantity', 0)} {item.get('unit', '')}")
        print(f"  Usage Time:  {item.get('usageStart', 'N/A')}")
        print("  " + "-"*66)

    if len(items) > 20:
        print(f"\n... and {len(items) - 20} more records")

    if allow_export:
        prompt_export(data, "usage data")

    input("\nPress Enter to continue...")

def display_daily_usage_data(data, from_date, to_date, allow_export=False):
    """Display daily usage data"""
    print(f"\n📊 Daily Usage from {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    print("="*70)

    if not isinstance(data, dict):
        print("❌ Unexpected data format")
        print(json.dumps(data, indent=2))
        input("\nPress Enter to continue...")
        return

    items = data.get('items', [])

    if not items:
        print("\n✓ No usage data found for this period")
        input("\nPress Enter to continue...")
        return

    print(f"\nFound {len(items)} daily usage records")
    print("="*70)

    # Group by day
    by_day = {}
    for item in items:
        day = item.get('usageDay', 'Unknown')
        if day not in by_day:
            by_day[day] = []
        by_day[day].append(item)

    for day in sorted(by_day.keys()):
        records = by_day[day]
        total_qty = sum((r.get('quantity') or 0) for r in records)
        print(f"\n📅 {day}")
        print(f"   Total Records: {len(records)}")
        print(f"   Total Quantity: {total_qty:,.2f}")

        # Show top services
        services = {}
        for r in records:
            svc = r.get('service', 'Unknown')
            services[svc] = services.get(svc, 0) + (r.get('quantity') or 0)

        for svc, qty in sorted(services.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"     - {svc}: {qty:,.2f}")

    if allow_export:
        prompt_export(data, "daily usage data")

    input("\nPress Enter to continue...")

def display_grouped_data(data, allow_export=False):
    """Display grouped usage data from API"""
    print("\n📊 Grouped Usage Data")
    print("="*70)

    if not isinstance(data, dict) or not data.get('success'):
        print("❌ Unexpected data format or request failed")
        print(json.dumps(data, indent=2))
        input("\nPress Enter to continue...")
        return

    rows = data.get('rows', [])
    metadata = data.get('metadata', {})

    print(f"\nDate Range: {metadata.get('fromDate', 'N/A')} to {metadata.get('toDate', 'N/A')}")
    print(f"Group By: {metadata.get('groupBy', 'N/A')}")
    print(f"Rows: {len(rows)}")
    print("="*70)

    if not rows:
        print("\n✓ No usage data found")
        input("\nPress Enter to continue...")
        return

    # Display first 20 rows
    for idx, row in enumerate(rows[:20], 1):
        print(f"\n[Row #{idx}]")
        for key, value in row.items():
            if value is not None:
                print(f"  {key:20s}: {value}")
        print("  " + "-"*66)

    if len(rows) > 20:
        print(f"\n... and {len(rows) - 20} more rows")

    if allow_export:
        prompt_export(data, "grouped data")

    input("\nPress Enter to continue...")

def display_daily_cost_data(data, from_date, to_date, allow_export=False):
    """Display daily cost data"""
    print(f"\n💰 Daily Cost Report from {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
    print("="*70)

    if not isinstance(data, dict):
        print("❌ Unexpected data format")
        print(json.dumps(data, indent=2))
        input("\nPress Enter to continue...")
        return

    items = data.get('items', [])

    if not items:
        print("\n✓ No cost data found for this period")
        input("\nPress Enter to continue...")
        return

    print(f"\nFound {len(items)} daily cost records")
    print("="*70)

    # Group by day and calculate totals
    by_day = {}
    total_cost = 0

    for item in items:
        day = item.get('usageDay', 'Unknown')
        cost = item.get('totalCost') or 0
        total_cost += cost

        if day not in by_day:
            by_day[day] = {'cost': 0, 'records': 0}
        by_day[day]['cost'] += cost
        by_day[day]['records'] += 1

    for day in sorted(by_day.keys()):
        info = by_day[day]
        print(f"\n📅 {day}")
        print(f"   Cost: ${info['cost']:>12,.4f}")
        print(f"   Records: {info['records']}")

    print("\n" + "="*70)
    print(f"💰 TOTAL COST: ${total_cost:,.4f}")
    print("="*70)

    if allow_export:
        prompt_export(data, "daily cost data")

    input("\nPress Enter to continue...")

def display_monthly_summary_data(data, allow_export=False):
    """Display monthly cost summary"""
    print("\n💰 Monthly Cost Summary")
    print("="*70)

    if not isinstance(data, dict):
        print("❌ Unexpected data format")
        print(json.dumps(data, indent=2))
        input("\nPress Enter to continue...")
        return

    items = data.get('items', [])

    if not items:
        print("\n✓ No cost data found")
        input("\nPress Enter to continue...")
        return

    # Group by month, then by tenant
    by_month = {}
    total_cost = 0

    for item in items:
        month = item.get('usageMonth', item.get('month', 'Unknown'))
        tenant = item.get('tenantId', 'N/A')
        cost = item.get('totalCost') or item.get('cost') or 0
        currency = item.get('currency', 'USD')

        total_cost += cost

        if month not in by_month:
            by_month[month] = []
        by_month[month].append({
            'tenant': tenant,
            'cost': cost,
            'currency': currency,
            'item': item
        })

    # Display grouped by month
    for month in sorted(by_month.keys()):
        tenants = by_month[month]
        month_total = sum(t['cost'] for t in tenants)

        print(f"\n📅 {month}")
        print(f"   Month Total: ${month_total:>12,.4f}")
        print(f"   Tenants: {len(tenants)}")
        print("   " + "-"*66)

        # Show each tenant
        for t in sorted(tenants, key=lambda x: x['cost'], reverse=True):
            tenant_label = t['tenant'] if t['tenant'] != 'N/A' else '(No Tenant)'
            print(f"      {tenant_label:20s}  ${t['cost']:>12,.4f}  {t['currency']}")

    print("\n" + "="*70)
    print(f"💰 GRAND TOTAL: ${total_cost:,.4f}")
    print("="*70)

    if allow_export:
        prompt_export(data, "monthly cost summary")

    input("\nPress Enter to continue...")

def display_monthly_service_summary_data(data, allow_export=False):
    """Display monthly cost summary by service"""
    print("\n💰 Monthly Cost by Service")
    print("="*70)

    if not isinstance(data, dict):
        print("❌ Unexpected data format")
        print(json.dumps(data, indent=2))
        input("\nPress Enter to continue...")
        return

    items = data.get('items', [])

    if not items:
        print("\n✓ No cost data found")
        input("\nPress Enter to continue...")
        return

    # Group by month
    by_month = {}
    total_cost = 0

    for item in items:
        month = item.get('usageMonth', item.get('month', 'Unknown'))
        service = item.get('service', 'Unknown')
        cost = item.get('totalCost') or item.get('cost') or 0
        total_cost += cost

        if month not in by_month:
            by_month[month] = {}
        if service not in by_month[month]:
            by_month[month][service] = 0
        by_month[month][service] += cost

    for month in sorted(by_month.keys()):
        services = by_month[month]
        month_total = sum(services.values())

        print(f"\n📅 {month} - Total: ${month_total:,.4f}")
        print("="*70)

        for service, cost in sorted(services.items(), key=lambda x: x[1], reverse=True):
            pct = (cost / month_total * 100) if month_total > 0 else 0
            print(f"  {service:30s}  ${cost:>12,.4f}  ({pct:>5.1f}%)")

    print("\n" + "="*70)
    print(f"💰 GRAND TOTAL: ${total_cost:,.4f}")
    print("="*70)

    if allow_export:
        prompt_export(data, "monthly service cost data")

    input("\nPress Enter to continue...")

# --------------------------------
# 🎯 MAIN MENU
# --------------------------------

templates = [
    ("Basic Compute Usage", create_basic_compute_usage),
    ("AI Chat Completion Usage", create_ai_chat_usage),
    ("Storage Usage", create_storage_usage),
    ("SaaS API Usage", create_saas_api_usage),
    ("SaaS Batch Processing", create_saas_batch_processing),
    ("Custom Usage Event", create_custom_usage),
]

print("\n" + "="*60)
print("🚀 AgenticBilling.AI - Usage Data Submission Tool")
print("="*60)
print(f"\n📡 Base URL: {BASE_URL}")
print(f"🔑 API Key: {'*' * (len(API_KEY) - 4) + API_KEY[-4:]}")
print(f"🏷️  Provider: {PROVIDER}")

def send_usage_data_menu():
    """Show send usage data submenu"""
    while True:
        print("\n" + "="*60)
        print("📤 SEND USAGE DATA")
        print("="*60)
        for idx, (name, _) in enumerate(templates, start=1):
            print(f"{idx}. {name}")
        print("0. Back to Main Menu")

        choice = input(f"\nSelect template (0-{len(templates)}): ").strip()

        if choice == '0':
            break

        if choice.isdigit() and 1 <= int(choice) <= len(templates):
            name, func = templates[int(choice) - 1]
            was_sent = send_usage_event(func, name)

            # After sending (or cancelling), ask if they want to continue
            if was_sent:
                print("\n" + "="*60)
                send_another = input("📤 Send another usage event? (y/N): ").strip().lower()
                if send_another != 'y':
                    break
            # If cancelled, just continue to show menu again
        else:
            print(f"❌ Invalid choice. Please select a number between 0 and {len(templates)}.")

while True:
    print("\n" + "="*60)
    print("📊 MAIN MENU")
    print("="*60)
    print("\n1. 📤 Send Usage Data")
    print("2. 📊 View Usage & Cost Data")
    print("0. Exit")

    choice = input("\nSelect option (0-2): ").strip()

    if choice == '0':
        break
    elif choice == '1':
        send_usage_data_menu()
    elif choice == '2':
        view_usage_data()
    else:
        print("❌ Invalid choice. Please select 0, 1, or 2.")

print("\n👋 Goodbye!")
