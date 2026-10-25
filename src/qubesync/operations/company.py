# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks company operations (``client.company``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict


if TYPE_CHECKING:
    from ..v2 import Client


class CompanyQueryParams(TypedDict, total=False):
    """Params for ``company.query`` (List companies)."""
    include_ret_element: List[Literal["AccountantCopy", "Address", "AddressBlock", "CompanyAddressBlockForCustomer", "CompanyAddressForCustomer", "CompanyEmailForCustomer", "CompanyName", "CompanyType", "CompanyWebSite", "DataExtRet", "EIN", "Email", "Fax", "FirstMonthFiscalYear", "FirstMonthIncomeTaxYear", "IsSampleCompany", "LegalAddress", "LegalCompanyName", "Phone", "SSN", "SubscribedServices", "TaxForm"]]
    #: `owner_id` identifies who owns the data extension. Use 0 for QuickBooks custom fields
    #: that appear in the UI, or use a GUID for private extensions owned by an app. Keep private
    #: GUIDs confidential unless you intentionally share extensions across apps. If you do share
    #: them, both apps must use the same `owner_id` and `data_ext_name`, because that pair
    #: uniquely identifies the extension.
    owner_id: List[str]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Company:
    """QuickBooks company operations: query.

    Get it from ``client.company``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[CompanyQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List companies.

        Queues ``company.query``: GET /connections/{connection_id}/companies, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``CompanyQueryParams``)::

            include_ret_element: List[Literal[...] (one of 22 values)]
            owner_id: List[str]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/companies/list-companies
        """
        return self._client._queue_operation("company.query", connection_id, params, webhook_url, idempotency_key)
