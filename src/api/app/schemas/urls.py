from pydantic.networks import Parts
from pydantic import AnyHttpUrl


class ProhibitedUploadHttpUrl(AnyHttpUrl):
    @classmethod
    def validate_host(cls, parts: "Parts") -> tuple[str, str | None, str, bool]:
        """Extend pydantic's AnyUrl validation to whitelist URL hosts."""
        host, tld, host_type, rebuild = super().validate_host(parts)
        if host not in {
            "florgon.ru",
            "florgon.com",
        }:
            raise ValueError(
                "Prohibited URL, only allowed URLs that is uploaded on the internal upload service (See documentation for uploading objects)"
            )

        return host, tld, host_type, rebuild
