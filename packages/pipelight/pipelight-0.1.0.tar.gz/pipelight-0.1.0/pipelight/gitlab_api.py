import click
import emoji
import gitlab
import os

def fetch_pipeline_status_and_time(gitlab_url):
    """
    ✨ Fetch the latest pipeline status and its updated_at timestamp.

    :param: URL for the GitLab instance that will be queried
    :return: A tuple of information about the pipeline that was identified (status, updated_at).
    """
    # Get GitLab token and project ID from environment variables
    gitlab_token = os.getenv('GITLAB_API_TOKEN')
    project_id = os.getenv('GITLAB_PROJECT_ID')
    if not gitlab_token:
        raise click.ClickException(emoji.emojize(":cross_mark_button: GITLAB_API_TOKEN environment variable not set"))
    if not project_id:
        raise click.ClickException(emoji.emojize(":cross_mark_button: GITLAB_PROJECT_ID environment variable not set"))
    gtlb = gitlab.Gitlab(gitlab_url, private_token=gitlab_token)
    try:
        project = gtlb.projects.get(project_id)
        # ℹ️ Get the latest pipeline in the list of pipelines | Explore alternate paths later
        pipelines = project.pipelines.list(per_page=1, get_all=False)
        if not pipelines:
            raise click.ClickException(emoji.emojize(":cross_mark_button: No pipelines found for the project"))
        latest_pipeline = pipelines[0]
        status = latest_pipeline.status
        updated_at = latest_pipeline.updated_at
        return status, updated_at
    except gitlab.exceptions.GitlabError as e:
        raise click.ClickException(emoji.emojize(f":fox: GitLab API error encountered: {str(e)}"))