# Generated from operations.json by scripts/generate_operations.py: don't edit.
"""QuickBooks form1099 category account mapping operations (``client.form1099_category_account_mapping``)."""

from typing import Any, Dict, List, Literal, Optional, TYPE_CHECKING, TypedDict

from ._types import (
    Ref,
)

if TYPE_CHECKING:
    from ..v2 import Client


class _MappingAccountRequired(TypedDict):
    #: `account_ref` points to an account in the company file. If both `full_name` and `list_id`
    #: are provided, `full_name` is ignored. Meaning depends on context: for checks it is the
    #: funding account; for ExpenseLineAdd it may be required by accounting preferences; for
    #: credit-card transactions it identifies the bank or card account involved.
    account_ref: Ref


class MappingAccount(_MappingAccountRequired, total=False):
    #: In some circumstances, changing the account mapping could result in the displaying of a
    #: user dialog in the QuickBooks UI prompting the user to confirm, which would prevent the
    #: SDK request from completing. Setting this property to true causes that user dialog to be
    #: suppressed.
    force_mapping: bool


class _CategoryAccountMappingModRequired(TypedDict):
    #: A mapping category indicates the form 1099 box that one or more accounts is being mapped
    #: to. You must specify one of the following enumerated values based on the form type:
    mapping_category: Literal["BOX1", "BOX10", "BOX13", "BOX14", "BOX2", "BOX3", "BOX4", "BOX5", "BOX6", "BOX7", "BOX8", "BOX9"]


class CategoryAccountMappingMod(_CategoryAccountMappingModRequired, total=False):
    mapping_account: List[MappingAccount]
    #: This is the dollar amount at which the IRS requires you to file the 1099-MISC and
    #: 1099-NEC forms. Each box (“Category” in SDK lingo) can have a separate threshold, as
    #: established by the IRS. For the latest thresholds, check the website for the Internal
    #: Revenue Service, currently at www.irs.gov.
    threshold: float


class Form1099CategoryAccountMappingQueryParams(TypedDict, total=False):
    """Params for ``form1099_category_account_mapping.query`` (List form1099 category account mappings)."""
    #: Added a form type to support Form 1099-NEC and Form 1099-MISC. `form_type` is a property
    #: to identify the type of form (MISC/NEC) for which Form1099CategoryAccountMapping query is
    #: run. Form type will be MISC if no `form_type` is specified.
    form_type: str
    #: A mapping category indicates the form 1099 box that one or more accounts is being mapped
    #: to. You must specify one of the following enumerated values based on the form type:
    mapping_category: List[Literal["BOX1", "BOX10", "BOX13", "BOX14", "BOX2", "BOX3", "BOX4", "BOX5", "BOX6", "BOX7", "BOX8", "BOX9"]]
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Form1099CategoryAccountMappingUpdateParams(TypedDict, total=False):
    """Params for ``form1099_category_account_mapping.update`` (Update form1099 category account mapping)."""
    category_account_mapping_mod: List[CategoryAccountMappingMod]
    #: This property reports only (it doesn’t set!) the current status of 1099 preferences
    #: setting in the company file. The value true indicates that the company file currently has
    #: the 1099 filing preference turned on. The value false indicates that the company file
    #: isn’t currently set to file 1099-MISC and 1099-NEC forms.
    is_filing1099_misc: bool
    #: Your own label for the request, sent to QuickBooks as its qbXML `requestID` and echoed in
    #: the raw answer (`response_xml`); optional, since the answer's webhook already carries the
    #: request's `id`.
    request_id: str


class Form1099CategoryAccountMapping:
    """QuickBooks form1099 category account mapping operations: query, update.

    Get it from ``client.form1099_category_account_mapping``. Each method queues the operation and returns the queued
    request; QuickBooks' answer comes to ``webhook_url`` as a webhook.
    """

    def __init__(self, client: "Client") -> None:
        self._client = client

    def query(
        self,
        connection_id: str,
        params: Optional[Form1099CategoryAccountMappingQueryParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """List form1099 category account mappings.

        Queues ``form1099_category_account_mapping.query``: GET /connections/{connection_id}/form1099-category-account-mappings, params in the query string.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``Form1099CategoryAccountMappingQueryParams``)::

            form_type: str
            mapping_category: List[Literal[...] (one of 12 values)]
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/form1099-category-account-mappings/list-form1099-category-account-mappings
        """
        return self._client._queue_operation("form1099_category_account_mapping.query", connection_id, params, webhook_url, idempotency_key)

    def update(
        self,
        connection_id: str,
        params: Optional[Form1099CategoryAccountMappingUpdateParams] = None,
        *,
        webhook_url: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update form1099 category account mapping.

        Queues ``form1099_category_account_mapping.update``: PUT /connections/{connection_id}/form1099-category-account-mappings, params as the JSON body.
        The answer comes to ``webhook_url`` in one webhook.
        Returns the queued request.

        Params (``Form1099CategoryAccountMappingUpdateParams``)::

            category_account_mapping_mod: List[CategoryAccountMappingMod]
                mapping_account: List[MappingAccount]
                    account_ref: Ref (required)
                        full_name: str
                        list_id: str
                    force_mapping: bool
                mapping_category: Literal[...] (one of 12 values) (required)
                threshold: float
            is_filing1099_misc: bool
            request_id: str

        Docs: https://docs.qubesync.com/api-reference/v2/form1099-category-account-mappings/update-form1099-category-account-mapping
        """
        return self._client._queue_operation("form1099_category_account_mapping.update", connection_id, params, webhook_url, idempotency_key)
