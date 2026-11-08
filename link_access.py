"""Optional UI privacy gate for revealing/copying stream URLs.

This is only a convenience privacy feature, NOT encryption, DRM, or a
security boundary. Public source/binaries can be inspected and PINs guessed.
"""

import hashlib
import hmac

# This stores a digest, not an advertised cleartext PIN.
_PIN_DIGEST = "8d23cf6c86e834a7aa6eded54c26ce2bb2e74903538c61bdd5d2197997ab2f72"


def verify_link_pin(value):
    if not isinstance(value, str):
        return False
    digest = hashlib.sha256(value.strip().encode("utf-8")).hexdigest()
    return hmac.compare_digest(digest, _PIN_DIGEST)
