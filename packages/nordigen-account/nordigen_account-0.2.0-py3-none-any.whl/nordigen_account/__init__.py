from nordigen import NordigenClient
from typing import Dict, Union, List, Optional, Tuple
from requests.exceptions import HTTPError


def create_nordigen_client(secret_id: str, secret_key: str, refresh_token: Optional[str] = None) -> Tuple[NordigenClient, str]:
    """
    Create and configure a NordigenClient instance using either a refresh token or by generating a new access token.

    Args:
        secret_id (str): Nordigen API secret ID.
        secret_key (str): Nordigen API secret key.
        refresh_token (str, optional): Refresh token to obtain the access token.

    Returns:
        Tuple[NordigenClient, Optional[str]]: Configured Nordigen client instance and the new refresh token if generated, else None.

    Raises:
        RuntimeError: If a new token cannot be generated.
        KeyError: If expected keys are missing from the token response.
    """
    status_invalid = 401
    new_refresh_token = None
    client = NordigenClient(secret_id=secret_id, secret_key=secret_key)

    try:
        if not refresh_token:
            # Generate new tokens if no refresh token is provided
            token_data = client.generate_token()
            new_refresh_token = token_data["refresh"]
        else:
            try:
                token_data = client.exchange_token(refresh_token)
            except HTTPError as http_err:
                response_data = http_err.response.json()
                status_code = response_data.get("status_code")

                if status_code == status_invalid:
                    # If refresh token is expired, generate a new token
                    token_data = client.generate_token()
                    new_refresh_token = token_data["refresh"]
                else:
                    raise RuntimeError(f"Error obtaining access token: {response_data}")

        access_token = token_data["access"]
        client.token = access_token

        return client, new_refresh_token

    except KeyError as key_err:
        raise KeyError(f"Missing expected key in token response: {str(key_err)}")

    except Exception as e:
        raise RuntimeError(f"Error obtaining access token: {str(e)}")


class BankAccount:
    """Representation of a Bank Account."""

    DetailsApiResponseType = Dict[
        str, Dict[str, str]
    ]
    BalancesApiResponseType = Dict[
        str, List[Dict[str, Union[Dict[str, str], str, bool]]]
    ]

    def __init__(
            self, client: NordigenClient, account_id: str, fetch_data: bool = False
    ) -> None:
        """
        Initialize a BankAccount object.

        Args:
            client (NordigenClient): An authenticated Nordigen client instance.
            account_id (str): The unique account ID.
            fetch_data (bool): Whether to fetch account details and balances on initialization.
        """
        self._client = client
        self._account_id = account_id

        # Initialize placeholders for account and balance data
        self.name = None
        self.status = None
        self.currency = None
        self.balances: List[Dict[str, Union[str, float]]] = []

        # Fetch data if the flag is set
        if fetch_data:
            self.update_account_data()
            self.update_balance_data()

    def update_account_data(self) -> None:
        """
        Fetch and update basic account details.
        Public method intended for external use to refresh account details data.
        """
        try:
            details_response: BankAccount.DetailsApiResponseType = self._client.account_api(id=self._account_id).get_details()
            account_details = details_response.get("account", {})

            self.name = account_details.get("name", "Unknown")
            self.status = account_details.get("status", "Unknown")
            self.currency = account_details.get("currency", "Unknown")

        except Exception as e:
            raise RuntimeError(f"Error updating account details: {str(e)}")


    def update_balance_data(self) -> None:
        """
        Fetch and update balance information.
        Public method intended for external use to refresh account balance data.
        """
        try:
            balances_response: BankAccount.BalancesApiResponseType = self._client.account_api(id=self._account_id).get_balances()
            self.balances = []
            account_balances = balances_response.get("balances", [])

            for balance in account_balances:
                balance_data = {
                    "balanceType": balance.get("balanceType", "Unknown"),
                    "amount": float(balance.get("balanceAmount", {}).get("amount", 0.00)),
                    "currency": balance.get("balanceAmount", {}).get("currency", "Unknown"),
                }
                self.balances.append(balance_data)

        except Exception as e:
            raise RuntimeError(f"Error updating account balances: {str(e)}")


class BankAccountManager:
    """Manager for handling multiple bank accounts."""

    STATUS_EXPIRED = "EX"

    RequisitionApiResponseType = Dict[
        str, Union[str, List[str], None, bool]
    ]

    def __init__(
            self, client: NordigenClient, requisition_id: str, fetch_data: bool = False
    ) -> None:
        """
        Initialize a BankAccountManager.

        Args:
            client (NordigenClient): An authenticated Nordigen client instance.
            requisition_id (str): The requisition ID to fetch linked accounts.
            fetch_data (bool): Whether to fetch account details and balances for all accounts on initialization.
        """
        self._client = client
        self._requisition_id = requisition_id
        self.accounts = []

        # Pass fetch_data to _initialize_accounts
        self._initialize_accounts(fetch_data)

    def _initialize_accounts(self, fetch_data: bool) -> None:
        """
        Initialize BankAccount objects for all linked accounts.

        Args:
            fetch_data (bool): Whether to fetch account details and balances on initialization of BankAccount object.

        Raises:
            ValueError: If the requisition status is expired or bank authorization may be incomplete.
            RuntimeError: If an unexpected error occurs while fetching accounts.
        """
        try:
            accounts_response = self._client.requisition.get_requisition_by_id(
                requisition_id=self._requisition_id
            )

            # Check if the requisition status is expired
            account_status = accounts_response.get("status")
            if account_status == self.STATUS_EXPIRED:
                raise ValueError(
                    "Access to accounts has expired as set in End User Agreement. Connect the accounts again with a new requisition."
                )

            # Retrieve list of account IDs linked to the requisition
            account_ids = accounts_response.get("accounts", [])
            # Check if the bank authorization has been completed
            if not account_ids:
                raise ValueError(
                    "No accounts found for the given requisition ID. Make sure you have completed authorization with a bank."
                )

            # Initialize a BankAccount instance and pass fetch_data for each account ID
            for account_id in account_ids:
                self.accounts.append(BankAccount(self._client, account_id, fetch_data=fetch_data))

        except ValueError as ve:
            raise ve

        except Exception as e:
            raise RuntimeError(f"Error initializing BankAccountManager: {str(e)}")
