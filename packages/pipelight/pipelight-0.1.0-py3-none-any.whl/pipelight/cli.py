import click
import emoji
from dotenv import load_dotenv
from .gitlab_api import fetch_pipeline_status_and_time
from .govee_api import update_govee_light_color, update_govee_light_brightness
from .utils import determine_light_color, calculate_temperature_and_brightness, get_govee_device_info
@click.group()
@click.version_option()
def cli():
    """
    ✨Change smart lights based on CI pipeline status
    """

@cli.command(name="change_the_lights")
@click.option('--gitlab-url', default='https://gitlab.com', show_default=True, help='URL of the GitLab instance')
def change_the_lights(gitlab_url):
    """
    ✨ The main loop for PIPELIGHT

    Retrieve status and "updated_at" for the latest pipeline in a particular project
    Calculate a color and brightness based on the status and "updated_at"
    Update the smart light based on this information

    :param: URL for the GitLab instance that will be queried, defaults to https://gitlab.com.
    """
    # 🔬 Gather variables for this environment
    load_dotenv()
    # 🔭 Get the status and "updated_at" for the most recently created pipeline
    pipeline_status, pipeline_updated_at = fetch_pipeline_status_and_time(gitlab_url)
    # 🎨 Determine what color to set the light to based on the pipeline status
    color_rgb = determine_light_color(pipeline_status)
    # ☀️ Determine how bright the light should be based on how recently the pipeline finished
    ## 🔎 More recent = brighter light
    light_brightness = calculate_temperature_and_brightness(pipeline_updated_at)
    # 💡 Collect the Govee SKU and Device information
    govee_sku, govee_device = get_govee_device_info()
    click.echo(emoji.emojize(f":rocket: The latest pipeline was {pipeline_status} so we will set the light to {color_rgb}!"))
    # 🌈 Set the color
    update_govee_light_color(govee_sku, govee_device, color_rgb)
    # 🚀 Set the brightness
    update_govee_light_brightness(govee_sku, govee_device, light_brightness)