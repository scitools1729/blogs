# Security & Infrastructure Impact Report
**Target Environment:** HPC Cluster (Slurm) with Rootless Podman and Shared Network File System (e.g., NFS, Lustre)
**Application:** Agentic evaluations using Inspect AI (`inspect_swe` + `inspect_harbor`) via `smoke_test.py`

---

## 1. Executive Summary
This document outlines the security and infrastructure footprint of executing `smoke_test.py` (an AI agent evaluation script) on a shared HPC cluster. 

The primary concerns typically raised by system administrators regarding containerized agentic evaluations are:
1. **Security/Privilege Escalation:** Will the container grant the AI agent elevated privileges on the host?
2. **Infrastructure Impact (IOPS/Inode Exhaustion):** Will the container hammer the shared HPC network file system with metadata requests (e.g., cloning massive repositories or generating thousands of temporary files)?

**Conclusion:** The configuration used in `smoke_test.py` is exceptionally safe. It operates entirely unprivileged using strict rootless user namespaces and completely bypasses the shared network file system for internal IO operations by utilizing an isolated overlay filesystem.

---

## 2. Security and Privilege Isolation

### Rootless Podman and `userns="keep-id"`
The evaluation runs inside a rootless Podman sandbox. There is no background system daemon (like the Docker daemon) running as `root`. The container processes are strictly bound to the invoking user's permissions.

Furthermore, we explicitly enforce `userns="keep-id"` in the Podman configuration.
* **Default Rootless Risk:** By default, rootless Podman simulates a "root" user inside the container by mapping the host user to UID 0 internally. 
* **The `keep-id` Mitigation:** By enabling `keep-id`, the host user (e.g., UID `26425`) is mapped to the exact same UID *inside* the container. The AI agent process runs as the unprivileged user both internally and externally. Even if an agent were to achieve container breakout, it strictly inherits the standard, unprivileged user access.

---

## 3. Storage and File System Impact

### Isolated Overlay File Systems vs. Host Mounts
A critical concern in HPC environments is protecting the shared network storage from high-IOPS applications.

> [!TIP]
> **No Host Mounts Used**
> The Inspect AI framework explicitly avoids using automatic host directory volume bindings (`-v` or `--mount`). 

Instead of binding a network directory to the container (which would route all container IO directly over the network to the storage server), Inspect AI uses a **one-time file provisioning** model combined with an **isolated overlay file system**.

### The File Provisioning Mechanism
1. **Overlay Creation:** Podman creates a temporary, layered "virtual" hard drive. The active "scratch" layer is stored locally on the compute node (typically in `~/.local/share/containers` or `/tmp`), bypassing the network storage entirely.
2. **Data Streaming:** Inspect AI gathers necessary configuration files from the host, zips them into a `.tar` archive in memory, and streams them through the container's background socket. 
3. **Execution:** The archive is unzipped inside the container's localized overlay. From this point on, the files are completely severed from the host machine. 
4. **Cleanup:** When the task completes, the container is destroyed, and the entire overlay file system instantly vanishes.

### File Generation Footprint
Because all file reads, writes, and modifications performed by the AI agent occur entirely on the compute node's fast, localized overlay storage, **there is zero risk of IOPS degradation or inode exhaustion on the shared HPC network file system.**

Furthermore, the specific payload of `smoke_test.py` is trivial:
* **The `hello_world` Dataset:** It does not clone any external git repositories or construct large virtual environments.
* **The `mini_swe_agent`:** The agent executes a basic sequence of bash commands to solve the puzzle, generating a single `hello.txt` file within the overlay filesystem.

---

## 4. Summary for System Administrators

The `smoke_test.py` execution profile is completely safe for deployment on a shared HPC cluster. 

* **No Privilege Escalation:** It executes entirely within the bounds of a standard, unprivileged user via rootless Podman.
* **No Metadata Bottlenecks:** It relies exclusively on localized container overlay filesystems, generating zero internal IOPS or metadata overhead on the shared network file system infrastructure.
