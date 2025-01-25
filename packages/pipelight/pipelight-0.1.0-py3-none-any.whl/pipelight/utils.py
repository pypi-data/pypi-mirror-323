from datetime import datetime, timezone, timedelta
import requests
import json
import click
import emoji
import os

def determine_light_color(status):
    """
    Determines the color the light should be based on the pipeline status.

    :param status: The pipeline status (e.g., 'success', 'failed', 'running').
    :return: The RGB color value to use for the provided status.
    """
    color_map = {
        "created": "#9F9110",                  # getting ready yellow
        "waiting_for_resource": "#DC6BAD",     # light purplish pink
        "preparing": "#9F9110",                # getting ready yellow
        "pending":"#9F9110",                   # getting ready yellow
        "running": "#3974C6",                  # in progress blue
        "success": "#309508",                  # success green
        "failed": "#FF0000",                   # error red
        "canceled": "#212121",                 # never mind gray
        "skipped": "#212121",                   # never mind gray
    }
    color = color_map.get(status, "#FFFFFF")
    color_rgb = int(color.lstrip('#'), 16)
    return color_rgb  # Default to white if status is unknown

def calculate_temperature_and_brightness(updated_at):
    """
    Calculates the temperature and brightness the light should be based on how recently the pipeline was updated.
    The more recently the pipeline was updated, the brighter the light will be. This makes more of a difference
    for side projects that might have a lot of pipelines.

    :param updated_at: The datetime when the pipeline was last updated (string format).
    :return: A tuple (temperature, brightness).
    """
    # time and date calculations
    updated_at = datetime.fromisoformat(updated_at)
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    delta = now - updated_at

    # The Govee API docs tell us that the temperature can range from 2000 to 9000
    if delta < timedelta(minutes=5):
        temperature = 9000
        brightness = 100
    elif delta < timedelta(minutes=15):
        temperature = 7000
        brightness = 90
    elif delta < timedelta(hours=1):
        temperature = 5000
        brightness = 75
    elif delta < timedelta(days=1):
        temperature = 4000
        brightness = 50
    elif delta < timedelta(weeks=1):
        temperature = 3000
        brightness = 30
    else:
        temperature = 2000
        brightness = 10
    return temperature, brightness

# Centralized function for sending API requests and handling errors
def send_govee_request(url, headers, payload):
    """
    Send a request to the Govee API and handle errors.

    :param url: The Govee API endpoint to use for this call. (All values today are the same.)
    :param headers: The HTTP headers to pass along with this request, this is how authentication to the Govee API is handled.
    :param payload:  The payload for the POST request to the Govee API.
    """
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            click.echo(emoji.emojize(":trophy: The light has been updated!"))
        elif response.status_code == 400:
            click.echo(emoji.emojize(
                ":warning: Error: A required parameter is missing. Check the payload and try again."))
        elif response.status_code == 404:
            click.echo(emoji.emojize(":x: Error: Device not found. Check the device ID and try again."))
        elif response.status_code == 429:
            click.echo(emoji.emojize(
                ":stopwatch: You hit the Govee API request limit of 10000 requests per account per day. Try again later."))
        else:
            click.echo(emoji.emojize(f":warning: Unexpected error: {response.status_code} - {response.text}"))
    except requests.exceptions.SSLError as e:
        click.echo(emoji.emojize(f":fox: SSL Error: {str(e)} - Check your SSL certificate or try again later."))
    except requests.exceptions.RequestException as e:
        click.echo(emoji.emojize(f":warning: : {str(e)}"))

def get_govee_device_info():
    """
    Fetches the device information (Govee SKU, Device ID) and sets up headers.

    :return: A tuple (Govee SKU, device).
    """
    # Get the device information from environment variables
    sku = os.getenv("GOVEE_DEVICE_MODEL")
    device = os.getenv("GOVEE_DEVICE_ID")
    if not sku or not device:
        raise ValueError(emoji.emojize(":crying_cat: The Govee Device SKU or ID is missing from the environment variables."))
    return sku, device