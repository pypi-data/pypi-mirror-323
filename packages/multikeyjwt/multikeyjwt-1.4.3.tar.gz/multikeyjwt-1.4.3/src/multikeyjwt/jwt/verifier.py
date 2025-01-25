"""Verifier for JWTs, using multiple public keys"""
from typing import Optional, Any, Dict, MutableSequence, ClassVar
from dataclasses import dataclass, field
from pathlib import Path
import functools
import logging
import urllib.request
import warnings
import tempfile
import ssl

import jwt as pyJWT  # too easy to accidentally override the module
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from cryptography.hazmat.backends import default_backend


from .common import JWTVerifierConfig
from ..config import ENVCONFIG

LOGGER = logging.getLogger(__name__)


@dataclass
class Verifier:
    """Helper/handler JWT verification"""

    config: JWTVerifierConfig = field(default_factory=JWTVerifierConfig)

    pubkeypath: Path = field(default_factory=functools.partial(ENVCONFIG, "JWT_PUBKEY_PATH", cast=Path))

    # Non-init public props
    pubkeys: MutableSequence[PublicKeyTypes] = field(init=False)

    # private
    _singleton: ClassVar[Optional["Verifier"]] = None

    def __post_init__(self) -> None:
        """Read the keys"""
        if not self.pubkeypath.exists():
            raise ValueError(f"{self.pubkeypath} does not exist")
        if self.pubkeypath.is_dir():
            self.pubkeys = []
            for fpth in self.pubkeypath.iterdir():
                if not fpth.is_file():
                    continue
                if not fpth.name.endswith(".pub"):
                    continue
                self.load_key(fpth)
        else:
            LOGGER.info("Loading key {}".format(self.pubkeypath))
            with self.pubkeypath.open("rb") as fpntr:
                self.pubkeys = [serialization.load_pem_public_key(fpntr.read(), backend=default_backend())]

    def load_key(self, fpth: Path) -> None:
        """Load given file into public keys"""
        LOGGER.debug("Loading key {}".format(fpth))
        self.pubkeys.append(serialization.load_pem_public_key(fpth.read_bytes(), backend=default_backend()))

    def load_key_from_url(self, url: str, timeout: float = 2.0, ssl_ctx: Optional[ssl.SSLContext] = None) -> None:
        """Save the url into a temporary file and load it"""
        if not url.startswith("https://") and not url.startswith("file://"):
            warnings.warn(f"Non-file {url} does not start with https")
        with urllib.request.urlopen(url, timeout=timeout, context=ssl_ctx) as response:  # nosec
            with tempfile.NamedTemporaryFile() as fpntr:
                fpntr.write(response.read())
                fpntr.flush()
                self.load_key(Path(fpntr.name))

    def decode(self, token: str) -> Dict[str, Any]:
        """Decode the token"""
        last_exception = Exception("This should not be raised")
        for pubkey in self.pubkeys:
            try:
                return pyJWT.decode(jwt=token, key=pubkey, algorithms=[self.config.algorithm])  # type: ignore
            except pyJWT.InvalidSignatureError as exc:
                last_exception = exc
                continue
        raise last_exception

    @classmethod
    def singleton(cls, **kwargs: Any) -> "Verifier":
        """Get a singleton"""
        if Verifier._singleton is None:
            Verifier._singleton = Verifier(**kwargs)
        assert Verifier._singleton is not None
        return Verifier._singleton
