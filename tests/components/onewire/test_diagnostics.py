"""Test 1-Wire diagnostics."""
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest

from homeassistant.components.diagnostics import REDACTED
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from . import setup_owproxy_mock_devices

from tests.components.diagnostics import get_diagnostics_for_config_entry


@pytest.fixture(autouse=True)
def override_platforms() -> Generator[None, None, None]:
    """Override PLATFORMS."""
    with patch("homeassistant.components.onewire.PLATFORMS", [Platform.SWITCH]):
        yield


DEVICE_DETAILS = {
    "device_info": {
        "identifiers": [["onewire", "EF.111111111113"]],
        "manufacturer": "Hobby Boards",
        "model": "HB_HUB",
        "name": "EF.111111111113",
    },
    "family": "EF",
    "id": "EF.111111111113",
    "path": "/EF.111111111113/",
    "type": "HB_HUB",
}


@pytest.mark.parametrize("device_id", ["EF.111111111113"], indirect=True)
async def test_entry_diagnostics(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    hass_client,
    owproxy: MagicMock,
    device_id: str,
) -> None:
    """Test config entry diagnostics."""
    setup_owproxy_mock_devices(owproxy, Platform.SENSOR, [device_id])
    await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert await get_diagnostics_for_config_entry(hass, hass_client, config_entry) == {
        "entry": {
            "data": {
                "host": REDACTED,
                "port": 1234,
            },
            "options": {
                "device_options": {
                    "28.222222222222": {"precision": "temperature9"},
                    "28.222222222223": {"precision": "temperature5"},
                }
            },
            "title": "Mock Title",
        },
        "devices": [DEVICE_DETAILS],
    }
