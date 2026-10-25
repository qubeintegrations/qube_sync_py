# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks preferences operations (``client.preferences``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class AccountingPreferencesMod(TypedDict, total=False):
    closing_date: str
    closing_date_password: str


class PreferencesQueryParams(TypedDict, total=False):
    """Params for ``preferences.query`` (List preferences)."""
    include_ret_element: List[Literal["AccountingPreferences", "CurrentAppAccessRights", "FinanceChargePreferences", "ItemsAndInventoryPreferences", "JobsAndEstimatesPreferences", "MultiCurrencyPreferences", "MultiLocationInventoryPreferences", "PurchasesAndVendorsPreferences", "ReportsPreferences", "SalesAndCustomersPreferences", "SalesTaxPreferences", "TimeTrackingPreferences"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class _PreferencesUpdateParamsRequired(TypedDict):
    accounting_preferences_mod: AccountingPreferencesMod


class PreferencesUpdateParams(_PreferencesUpdateParamsRequired, total=False):
    """Params for ``preferences.update`` (Update preferences)."""
    include_ret_element: List[Literal["AccountingPreferences", "CurrentAppAccessRights", "FinanceChargePreferences", "ItemsAndInventoryPreferences", "JobsAndEstimatesPreferences", "MultiCurrencyPreferences", "MultiLocationInventoryPreferences", "PurchasesAndVendorsPreferences", "ReportsPreferences", "SalesAndCustomersPreferences", "SalesTaxPreferences", "TimeTrackingPreferences"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Preferences:
    """QuickBooks preferences operations: query, update.

    Get it from ``client.preferences``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[PreferencesQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List preferences.

        Queues ``preferences.query``: GET /connections/{connection_id}/preferences, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PreferencesQueryParams``)::

            include_ret_element: List[Literal[...] (one of 12 values)]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/preferences/list-preferences
        """
        return self._client._queue_operation("preferences.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[PreferencesUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update preferences.

        Queues ``preferences.update``: PUT /connections/{connection_id}/preferences, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``PreferencesUpdateParams``)::

            accounting_preferences_mod: AccountingPreferencesMod (required)
                closing_date: str
                closing_date_password: str
            include_ret_element: List[Literal[...] (one of 12 values)]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/preferences/update-preferences
        """
        return self._client._queue_operation("preferences.update", connection_id, params, webhook_url, idempotency_key)
