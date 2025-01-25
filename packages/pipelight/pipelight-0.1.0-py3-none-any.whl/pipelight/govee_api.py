import os
import uuid
from .utils import send_govee_request

def update_govee_light_brightness(sku, device, brightness):
    """
    ✨ Update the brightness of a particular Govee light via the REST

    :param: Govee SKU for the light to update
    :param: Govee Device ID (unique identifier) for the light to update
    :param: The brightness to set
    """
    url = "https://openapi.api.govee.com/router/api/v1/device/control"
    headers = {
        "Govee-API-Key": os.getenv("GOVEE_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "requestId": str(uuid.uuid4()),
        "payload": {
            "sku": sku,
            "device": device,
            "capability": {
                "type": "devices.capabilities.brightness",
                "instance": "brightness",
                "value": brightness,
                }
            }
        }
    send_govee_request(url, headers, payload)

def update_govee_light_color(sku, device, color_rgb):
    """
    ✨ Update the color of a particular Govee light via the REST API

    :param: Govee SKU for the light to update
    :param: Govee Device ID (unique identifier) for the light to update
    :param: The color to set
    """
    url = "https://openapi.api.govee.com/router/api/v1/device/control"
    headers = {
        "Govee-API-Key": os.getenv("GOVEE_API_KEY"),
        "Content-Type": "application/json"
    }
    payload = {
        "requestId": str(uuid.uuid4()),
        "payload": {
            "sku": sku,
            "device": device,
            "capability": {
                "type": "devices.capabilities.color_setting",
                "instance": "colorRgb",
                "value": color_rgb,
                }
            }
        }
    send_govee_request(url, headers, payload)