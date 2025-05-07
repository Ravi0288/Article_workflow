import os
import shutil
import requests
import re
from urllib.parse import urlparse
from pathlib import Path

def retrieve_manuscripts(path_name: str, manuscript_file: dict, support_files: list[dict]) -> str:
    os.makedirs(path_name, exist_ok=True)
    message = ""

    # Handle primary Manuscript file
    manuscript_url = manuscript_file.get('URL')
    if manuscript_url:
        parsed_url = urlparse(manuscript_url)
        suffix = Path(parsed_url.path).suffix
        dest_path = os.path.join(path_name, f"MANUSCRIPT{suffix}")

        try:
            if parsed_url.scheme in ['http', 'https']:
                response = requests.get(manuscript_url)
                if response.status_code == 200:
                    with open(dest_path, 'wb') as f:
                        f.write(response.content)
                else:
                    message += "missing manuscript file; "
            elif parsed_url.scheme == 'file':
                local_path = parsed_url.path
                if os.path.exists(local_path):
                    shutil.copy2(local_path, dest_path)
                else:
                    message += "missing manuscript file; "
            else:
                message += "unsupported manuscript URL scheme; "
        except Exception as e:
            message += f"error retrieving manuscript: {e}; "
    else:
        message += "missing manuscript file; "

    # Handle Support Manuscript files
    file_kinds = {
        'MANUSCRIPT-SUPPORT': re.compile(r'support', re.IGNORECASE),
        'NON-PUBLIC': re.compile(r'non-?public', re.IGNORECASE),
        'DATASET': re.compile(r'dataset', re.IGNORECASE),
        'DOCUMENT': re.compile(r'.*', re.IGNORECASE),  # default fallback
    }

    file_counters = {}
    missing_supports = 0

    for support in support_files:
        url = support.get('url')
        label = support.get('label', '')
        parsed_url = urlparse(url) if url else None

        if not parsed_url:
            missing_supports += 1
            continue

        suffix = Path(parsed_url.path).suffix
        base_name = None

        for kind, pattern in file_kinds.items():
            if pattern.search(label):
                base_name = kind
                break

        if not base_name:
            base_name = 'DOCUMENT'

        file_counters.setdefault((base_name, suffix), 1)
        count = file_counters[(base_name, suffix)]

        if count == 1:
            file_name = f"{base_name}{suffix}"
        else:
            file_name = f"{base_name}-{count:03d}{suffix}"

        dest_path = os.path.join(path_name, file_name)

        try:
            if parsed_url.scheme in ['http', 'https']:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(dest_path, 'wb') as f:
                        f.write(response.content)
                    file_counters[(base_name, suffix)] += 1
                else:
                    missing_supports += 1
            elif parsed_url.scheme == 'file':
                local_path = parsed_url.path
                if os.path.exists(local_path):
                    shutil.copy2(local_path, dest_path)
                    file_counters[(base_name, suffix)] += 1
                else:
                    missing_supports += 1
            else:
                missing_supports += 1
        except Exception:
            missing_supports += 1

    if missing_supports:
        message += f"missing {missing_supports} supporting file(s); "

    return "Successful" if not message else message.strip()
