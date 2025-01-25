from cubicweb.entities import AnyEntity, fetch_config


class AuthToken(AnyEntity):
    __regid__ = "AuthToken"
    fetch_attrs, cw_fetch_order = fetch_config(["id", "enabled", "expiration_date"])

    def dc_title(self):
        return self.id

    def dc_description(self):
        return (
            f"{self.id} ({self.enabled and 'enabled' or 'disabled'}) "
            f"expires on {self.expiration_date}"
        )
