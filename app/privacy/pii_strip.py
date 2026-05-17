"""
BOLDR Self-Improving Customer Intelligence Engine
PII Stripping Module — Configurable personally identifiable information redaction

When enabled (PII_STRIP_ENABLED=true in .env), this module strips emails,
phone numbers, and personal names from messages before they enter the
intelligence pipeline. This ensures GDPR/PDPA compliance and prevents
sensitive customer data from persisting in logs, theme clusters, or KB.

Author: Steve Ng, Founder and CEO — Digital Futures Consultancy LLP
"""

import os
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Configurable via environment variable — default is OFF for competition demo
PII_STRIP_ENABLED = os.environ.get("PII_STRIP_ENABLED", "false").lower() in ("true", "1", "yes")

# PII patterns (Singapore/international)
PATTERNS = {
    # Email addresses: john@example.com, "John Doe" <john@example.com>
    "email": re.compile(
        r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    ),
    # Phone numbers: +65 9123 4567, +65-9123-4567, +6591234567, 91234567, 9123 4567
    "phone_sg": re.compile(
        r'(?:\+65[\s\-]?)?(?:[89]\d{3}[\s\-]?\d{4})|(?:\+65[\s\-]?\d{4}[\s\-]?\d{4})',
    ),
    # International phone: +1-234-567-8901, +44 20 7946 0958
    "phone_intl": re.compile(
        r'\+\d{1,3}[\s\-]?\(?\d{1,4}\)?[\s\-]?\d{1,4}[\s\-]?\d{1,4}[\s\-]?\d{0,4}',
    ),
    # NRIC/FIN (Singapore): S1234567A, T1234567B, F1234567C, G1234567D
    "nric": re.compile(
        r'\b[STFGstfg]\d{7}[A-Za-z]\b',
    ),
    # Credit card numbers (basic pattern): 4111 1111 1111 1111, 4111-1111-1111-1111
    "credit_card": re.compile(
        r'\b(?:\d{4}[\s\-]){3}\d{4}\b',
    ),
    # Singapore postal codes: 6-digit starting with 0-8
    "postal_sg": re.compile(
        r'\b[0-8]\d{5}\b',
    ),
    # Common name patterns in email headers: "John Doe" <...>
    "name_in_email": re.compile(
        r'"([^"]+)"\s*<[^>]+>',
    ),
    # URLs that might contain query params with PII
    "url_with_params": re.compile(
        r'https?://[^\s<>"\']+[\?&](?:email|phone|name|user|id)=([^\s&<>"\']+)',
        re.IGNORECASE,
    ),
}

# Redaction labels
LABELS = {
    "email": "[EMAIL_REDACTED]",
    "phone_sg": "[PHONE_REDACTED]",
    "phone_intl": "[PHONE_REDACTED]",
    "nric": "[NRIC_REDACTED]",
    "credit_card": "[CARD_REDACTED]",
    "postal_sg": "[POSTAL_REDACTED]",
    "name_in_email": "[NAME_REDACTED]",
    "url_with_params": "[URL_REDACTED]",
}


def strip_pii(text: str, enabled: Optional[bool] = None) -> str:
    """Strip personally identifiable information from text.

    Args:
        text: Input text that may contain PII.
        enabled: Override for the PII_STRIP_ENABLED env var.
                 If None, uses the env var (default: false).
                 If True/False, forces enable/disable.

    Returns:
        Text with PII replaced by redaction labels.
        Returns original text if PII stripping is disabled.
    """
    should_strip = enabled if enabled is not None else PII_STRIP_ENABLED

    if not should_strip or not text:
        return text

    redacted = text

    # Process in specific order to avoid double-redaction
    # 1. Name in email headers first (most specific pattern)
    for match in PATTERNS["name_in_email"].finditer(redacted):
        full_match = match.group(0)
        redacted = redacted.replace(full_match, LABELS["name_in_email"], 1)

    # 2. Credit card numbers (before phone, as CCs contain digits)
    redacted = PATTERNS["credit_card"].sub(LABELS["credit_card"], redacted)

    # 3. NRIC/FIN (Singapore specific, before postal codes)
    redacted = PATTERNS["nric"].sub(LABELS["nric"], redacted)

    # 4. Phone numbers (international first, then SG-specific)
    redacted = PATTERNS["phone_intl"].sub(LABELS["phone_sg"], redacted)
    redacted = PATTERNS["phone_sg"].sub(LABELS["phone_sg"], redacted)

    # 5. Email addresses
    redacted = PATTERNS["email"].sub(LABELS["email"], redacted)

    # 6. URLs with PII in query params
    for match in PATTERNS["url_with_params"].finditer(redacted):
        full_match = match.group(0)
        redacted = redacted.replace(full_match, LABELS["url_with_params"], 1)

    # 7. Singapore postal codes (careful not to redact order IDs, ticket IDs, etc.)
    # Only redact 6-digit numbers starting with 0-8 that are NOT part of ticket/order IDs
    for match in PATTERNS["postal_sg"].finditer(redacted):
        # Skip if preceded by TKT- or # (ticket/order ID)
        start = match.start()
        if start > 0 and redacted[start-1] in ('-', '#'):
            continue
        redacted = redacted[:start] + LABELS["postal_sg"] + redacted[match.end():]

    return redacted


def get_pii_stats(text: str, enabled: Optional[bool] = None) -> dict:
    """Get statistics about PII found in text (for audit logging).

    Args:
        text: Input text to scan.
        enabled: Override for PII_STRIP_ENABLED.

    Returns:
        Dict with counts of each PII type found.
    """
    should_strip = enabled if enabled is not None else PII_STRIP_ENABLED

    if not should_strip or not text:
        return {"pii_stripping_enabled": should_strip, "total_redactions": 0}

    stats = {"pii_stripping_enabled": True}
    total = 0

    for pii_type, pattern in PATTERNS.items():
        count = len(pattern.findall(text))
        if count > 0:
            stats[pii_type] = count
            total += count

    stats["total_redactions"] = total
    return stats


def is_pii_stripping_enabled() -> bool:
    """Check if PII stripping is currently enabled."""
    return PII_STRIP_ENABLED