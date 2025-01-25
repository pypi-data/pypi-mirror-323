# MorphCloud Python SDK 

## Overview

MorphCloud is a platform designed to spin up remote AI devboxes we call runtimes.
It provides a suite of code intelligence tools and a Python SDK to manage, create, delete, and interact with runtime instances.

## Setup Guide

### Prerequisites

Python 3.11 or higher

Go to [https://cloud.morph.so](https://cloud.morph.so/web/api-keys), log in with the provided credentials and create an API key.

Set the API key as an environment variable  `MORPH_API_KEY`.

### Installation

```
pip install morphcloud
```

Export the API key:

```
export MORPH_API_KEY="your-api-key"
```

## Python API

The SDK provides a Python API to interact with the MorphCloud API.

The following example creates a minimal vm snapshot, starts and instance then sets up a simple HTTP server and makes an HTTP request to it.

```py
import time
import requests
import tempfile
from morphcloud.api import MorphCloudClient

# Connect to the MorphCloud API
# The API key can be set through the client or as an environment variable MORPH_API_KEY
client = MorphCloudClient()

# Create a snapshot with 1 vCPU, 128MB memory, 700MB disk size, and the image "morphvm-minimal"
snapshot = client.snapshots.create(vcpus=1, memory=128, disk_size=700, image_id="morphvm-minimal")

# Start an instance from the snapshot and open an SSH connection
with client.instances.start(snapshot_id=snapshot.id) as instance, instance.ssh() as ssh:
    # Install uv and python using the ssh connection
    ssh.run(["curl -LsSf https://astral.sh/uv/install.sh | sh"]).raise_on_error()
    ssh.run(["echo 'source $HOME/.local/bin/env' >> $HOME/.bashrc"]).raise_on_error()
    ssh.run(["uv", "python", "install"]).raise_on_error()

    # Create an index.html file locally and copy it to the instance
    with tempfile.NamedTemporaryFile(mode="w") as f:
        f.writelines("<h1>Hello, World!</h1>")
        f.flush()
        ssh.copy_to(f.name, "index.html")

    # Start an HTTP server on the instance with a tunnel to the local machine and run it in the background
    with ssh.run(["uv", "run", "python3", "-m", "http.server", "8080", "--bind", "127.0.0.1"], background=True) as http_server, \
         ssh.tunnel(local_port=8888, remote_port=8080) as tunnel:

        # Wait for the HTTP server to start
        time.sleep(1)

        print("HTTP Server:", http_server.stdout)

        print("Making HTTP request")
        response = requests.get("http://127.0.0.1:8888", timeout=10)
        print("HTTP Response:", response.status_code)
        print(response.text)
```

## Command Line Interface

The SDK also provides a command line interface to interact with the MorphCloud API.
You can use the CLI to create, delete, and manage runtime instances.

### Images

List available images:
```bash
morph image list [--json]
```

### Snapshots

```bash
# List all snapshots
morph snapshot list [--json]

# Create a new snapshot
morph snapshot create --image-id <id> --vcpus <n> --memory <mb> --disk-size <mb> [--digest <hash>]

# Delete a snapshot
morph snapshot delete <snapshot-id>
```

### Instances

```bash
# List all instances
morph instance list [--json]

# Start a new instance from snapshot
morph instance start <snapshot-id> [--json]

# Stop an instance
morph instance stop <instance-id>

# Get instance details
morph instance get <instance-id>

# Create snapshot from instance
morph instance snapshot <instance-id> [--json]

# Clone an instance
morph instance branch <instance-id> [--count <n>]
```

### Instance Management

```bash
# Execute command on instance
morph instance exec <instance-id> <command>

# SSH into instance
morph instance ssh <instance-id> [command]

# Port forwarding
morph instance port-forward <instance-id> <remote-port> [local-port]

# Expose HTTP service
morph instance expose-http <instance-id> <name> <port>

# Hide HTTP service
morph instance hide-http <instance-id> <name>
```

### Interactive Chat

Start an interactive chat session with an instance:

**Note:** You'll need to set `ANTHROPIC_API_KEY` environment variable to use this command.

```bash
morph instance chat <instance-id> [instructions]
```

