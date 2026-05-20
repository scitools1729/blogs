# Technical Deep-Dive: ModelAudit

## Core Methodology

ModelAudit employs **Static Analysis** to evaluate machine learning models. Unlike dynamic analysis (sandboxing), which executes the model in an isolated environment to observe its behavior, static analysis parses the file format's underlying data structures, bytecodes, and configurations without ever loading the model into a runtime environment or importing ML frameworks like PyTorch or TensorFlow. This ensures the scanning process itself cannot be compromised by the model it is evaluating.

## How it Identifies Vulnerabilities

ModelAudit breaks down its scanning engine into format-specific analyzers. Here is the technical approach for the primary threat vectors:

### 1. Deserialization Attacks (Pickle, Joblib, Dill)
The most common ML attack vector is malicious Python `pickle` files (often ending in `.pt`, `.pth`, `.pkl`). The pickle format is essentially a stack-based virtual machine. 
* **Methodology:** ModelAudit implements a safe pickle opcode parser. Instead of unpickling the file (which executes the code), it reads the byte stream and analyzes the opcodes.
* **Detection:** It specifically flags dangerous opcodes like `REDUCE` (which executes a callable with arguments), `INST`, and `OBJ`. 
* **Target Identification:** It tracks the module and function references associated with these opcodes. If a pickle file attempts to import and execute `os.system`, `subprocess.Popen`, `eval`, or `exec`, the scanner immediately flags it as a `CRITICAL` threat indicating a Remote Code Execution (RCE) payload.

### 2. Framework-Specific Graph Analysis
For formats that define computational graphs rather than executable state (like ONNX, TensorFlow SavedModel, Keras H5):
* **Keras (`.h5`, `.keras`):** It parses the JSON/HDF5 structure to look for `Lambda` layers. Lambda layers allow arbitrary Python code to be embedded as a string and evaluated at runtime.
* **TensorFlow (`.pb`):** It parses the protobuf definition of the computation graph to identify suspicious or highly unusual operations that might indicate a backdoor or embedded payload.
* **ONNX:** It looks for custom operators or embedded JIT-compiled code that deviates from standard ONNX definitions.

### 3. Archive and Compression Exploits
Models are often distributed as archives (ZIP, Tar).
* **Methodology:** During the extraction or parsing phase, the scanner evaluates the compression ratios and directory structures.
* **Detection:** It identifies "Zip Bombs" (highly compressed files designed to exhaust memory/disk space upon extraction) and directory traversal attempts (e.g., paths containing `../`) designed to overwrite critical system files.

### 4. Embedded Secrets and Binaries
* **Methodology:** It utilizes pattern matching (Regex and entropy analysis) across the raw byte streams and extracted strings of the model artifacts.
* **Detection:** It detects embedded API keys, authentication tokens, private keys, and hardcoded network endpoints (IPs, URLs) that could be used for data exfiltration. It also flags magic bytes corresponding to compiled executables (Windows PE, Linux ELF, macOS Mach-O) hidden within the model weights.

## Performance and Large-Scale Studies

Currently, there are **no publicly available, peer-reviewed large-scale academic studies** specifically analyzing the efficacy of Promptfoo's ModelAudit engine. 

However, the foundational techniques it relies on (such as static opcode analysis of pickle files) are well-documented in the cybersecurity community:
* **Efficacy:** Static opcode analysis is highly effective at catching "script-kiddie" and standard RCE attacks embedded in models (which constitute the vast majority of HuggingFace malware).
* **False Positives:** The false-positive rate is generally low for deserialization attacks because standard ML models have no legitimate reason to invoke `os.system` during weight loading.
* **Limitations:** The primary technical limitation of this approach is vulnerability to heavy obfuscation. If an attacker crafts a highly complex, obfuscated payload that manipulates the pickle stack without directly importing obvious red-flag modules, static scanners can sometimes be bypassed. Advanced attacks targeting the mathematical weights themselves (e.g., embedding a neural backdoor that triggers on a specific pixel pattern) are mathematically invisible to static structural scanners like ModelAudit.

In summary, ModelAudit operates as an extremely fast, structural parser that excels at neutralizing the most common and devastating supply-chain attacks (RCE via deserialization) but is not designed to detect complex behavioral manipulation of the neural network itself.
