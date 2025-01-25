# 🚀 ✨ 🤖 💡 Pipelight

> Visualize CI pipeline status with smart lights

## 🗺️ Overview

With `pipelight`, your smart lights are automatically updated to reflect the status of the latest pipeline.

## 🛠️ Installation

```bash
pip install pipelight
```

## 📋 Configuration

Set these environment variables in `.env`:

```bash
GOVEE_API_KEY=goveetokenwouldgohere
GOVEE_DEVICE_ID=77:00:00:00:00:00:00:00
GOVEE_DEVICE_MODEL=HXXXX
GITLAB_API_TOKEN=glpatWOULDGOHERE
GITLAB_PROJECT_ID=0123456
```

## ✨ Features

### 🌈 Pipeline Status Colors

- 💛 Yellow (`#9F9110`): Created, Preparing, Pending
- 💗 Pink (`#DC6BAD`): Waiting for Resources
- 💙 Blue (`#3974C6`): Running
- 💚 Green (`#309508`): Success
- 💔 Red (`#FF0000`): Failed
- 🖤 Dark Gray (`#212121`): Canceled, Skipped

### 🌞 Adaptive Brightness

The brightness of the light changes based on how recently the pipeline was updated. More recent pipelines have a brighter color. The brightness progressively fades as the pipeline's `updated_at` value is less recent.

### 🦊 GitLab

There is support for checking any GitLab instance (`.com`, self-managed or GitLab Dedicated). By default, `pipelight` assumes `gitlab.com`.

## 🚀 Usage

Run the main command:

```bash
pipelight change-the-lights
```

Customize GitLab instance:

```bash
pipelight change-the-lights --gitlab-url https://gitlab.example.com
```

Use `uv`:

```bash
uv run --with emoji,python-dotenv,python-gitlab python -m pipelight change_the_lights
```

Run in a loop to continuously monitor a project's pipelines as you work:

```bash
while true ; do date ; uv run --with emoji,python-dotenv,python-gitlab python -m pipelight change_the_lights ; sleep 15 ; done
```

## 🚀 Publishing

```toml
[[tool.uv.index]]
name = "testpypi"
url = "https://test.pypi.org/simple/"
publish-url = "https://test.pypi.org/legacy/"
```

## 📄 License

MIT License