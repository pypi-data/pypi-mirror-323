import pytest
import responses

from logafault.faults import (
    FaultsAPIError,
    get_all_faults,
    log_fault_my_address,
    log_fault_other_address,
)
from logafault.models import (
    Address,
    ChildWorkTypes,
    CustomLookupCodes,
    FaultData,
    WorkTypes,
)

FAULTS_URL = "https://citypower.mobi/forcelink/za4/rest/calltakemanager"


class TestLogFaultMyAddress:
    def setup_method(self):
        self.url = f"{FAULTS_URL}/logCallMyAddress"
        self.cookie = "session_id=abcd1234"
        self.fault_data = FaultData(
            workType=WorkTypes.NS,
            childWorkType=ChildWorkTypes.NSTL,
            customLookupCode2=CustomLookupCodes.PREPAID,
            description="The traffic light at the intersection is off",
            custom2="1234567890",
            custom4="",
            contactNumber="0123456789",
            contactName="Bruce Wayne",
        )

    def test_log_fault_my_address_success_returns_data(self) -> None:
        mocked_response = {
            "result": "SUCCESS",
            "errorMessage": None,
            "successMessage": None,
            "code": "CPWEB1234567",
            "id": 4689356,
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json=mocked_response,
                status=200,
            )

            response = log_fault_my_address(self.cookie, self.fault_data)

            assert response == mocked_response

    def test_log_fault_my_address_success_calls_method_once(self) -> None:
        mocked_response = {
            "result": "SUCCESS",
            "errorMessage": None,
            "successMessage": None,
            "code": "CPWEB1234567",
            "id": 4689356,
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json=mocked_response,
                status=200,
            )

            _ = log_fault_my_address(self.cookie, self.fault_data)

            assert len(rsps.calls) == 1
            assert rsps.calls[0].request.headers["Cookie"] == self.cookie

    def test_log_fault_my_address_success_sends_cookie(self) -> None:
        mocked_response = {
            "result": "SUCCESS",
            "errorMessage": None,
            "successMessage": None,
            "code": "CPWEB1234567",
            "id": 4689356,
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json=mocked_response,
                status=200,
            )

            _ = log_fault_my_address(self.cookie, self.fault_data)

            assert rsps.calls[0].request.headers["Cookie"] == self.cookie

    def test_log_fault_my_address_http_error(self) -> None:
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json={"error": "Something went wrong"},
                status=500,
            )

            with pytest.raises(
                FaultsAPIError, match="Failed to log fault: 500 Server Error"
            ):
                log_fault_my_address(self.cookie, self.fault_data)


class TestLogFaultOtherAddress:
    def setup_method(self):
        self.url = f"{FAULTS_URL}/logCallOtherAddress"
        self.cookie = "session_id=abcd1234"
        self.fault_data = FaultData(
            workType=WorkTypes.NS,
            childWorkType=ChildWorkTypes.NSIP,
            customLookupCode2=CustomLookupCodes.LARGE_POWER_USER,
            description="No supply to Honeydew Manor",
            custom2="54295267373",
            custom4="",
            address=Address(
                address3="",
                address4="7",
                address5="Taylor Rd",
                address6="Honeydew",
                address7="Roodepoort",
                address8="1724",
            ),
            contactNumber="0821234567",
            contactName="John Doe",
        )

    def test_log_fault_other_address_success_returns_data(self) -> None:
        mocked_response = {
            "result": "SUCCESS",
            "errorMessage": None,
            "successMessage": None,
            "code": "CPWEB4506225",
            "id": 4778450,
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json=mocked_response,
                status=200,
            )

            response = log_fault_other_address(self.cookie, self.fault_data)

            assert response == mocked_response

    def test_log_fault_other_address_success_calls_method_once(self) -> None:
        mocked_response = {
            "result": "SUCCESS",
            "errorMessage": None,
            "successMessage": None,
            "code": "CPWEB4506225",
            "id": 4778450,
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json=mocked_response,
                status=200,
            )

            _ = log_fault_other_address(self.cookie, self.fault_data)

            assert len(rsps.calls) == 1
            assert rsps.calls[0].request.headers["Cookie"] == self.cookie

    def test_log_fault_other_address_success_sends_cookie(self) -> None:
        mocked_response = {
            "result": "SUCCESS",
            "errorMessage": None,
            "successMessage": None,
            "code": "CPWEB4506225",
            "id": 4778450,
        }

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json=mocked_response,
                status=200,
            )

            _ = log_fault_other_address(self.cookie, self.fault_data)

            assert rsps.calls[0].request.headers["Cookie"] == self.cookie

    def test_log_fault_other_address_http_error(self) -> None:
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.POST,
                self.url,
                json={"error": "Something went wrong"},
                status=500,
            )

            with pytest.raises(
                FaultsAPIError, match="Failed to log fault: 500 Server Error"
            ):
                log_fault_other_address(self.cookie, self.fault_data)


class TestGetAllFaults:
    def setup_method(self) -> None:
        self.url = f"{FAULTS_URL}/getAllCustomerCalls"
        self.cookie = "session_id=abcd1234"

    def test_get_all_faults_success(self):
        expected_faults = [
            {
                "id": 1262784,
                "code": "CPWEB1234567",
                "description": "No power in the Gotham area",
                "workType": "No Supply (Area)",
                "status": "Closed_CL",
                "dateCreated": 1530251597000,
                "contactName": "Bruce Wayne",
                "address": "224 Park Drive, Gotham City",
                "latitude": -26.54321,
                "longitude": 27.99999999999999,
            }
        ]

        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                self.url,
                json=expected_faults,
                status=200,
            )

            result = get_all_faults(self.cookie)
            assert result == expected_faults

    def test_get_all_faults_http_error(self) -> None:
        with responses.RequestsMock() as rsps:
            rsps.add(
                responses.GET,
                self.url,
                status=500,
            )

            with pytest.raises(
                FaultsAPIError,
                match="Failed to fetch faults: 500 Server Error: Internal Server Error for url",
            ):
                get_all_faults(self.cookie)
