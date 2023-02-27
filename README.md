<div align="center">
  <h1>
    <img src="https://raw.githubusercontent.com/Fleshgrinder/python-protoc-exe/main/.idea/icon.svg" height="36" width="75" alt="Protobuf Logo"><br>
    Python Protoc Executable
  </h1>
  <p><b>PyPI packaged Protocol Buffers Compiler</b></p>
</div>

A PyPI package providing a pip-installable [protoc] executable.

This package does not provide any Python code, it provides just the unaltered
`protoc` executable. The versioning thus also follows the official versioning
of `protoc`, and is different to the versioning of the [protobuf] runtime.

The difference of this package to [protoc-wheel] and [protoc-wheel-0] is that
those packages wrap the `protoc` in Python. Whereas this package provides just
the `protoc` executable, without anything else. As a consequence you can
directly call `protoc` after installing this package in your environment. This
makes it perfect for providing the `protoc` executable wherever you need the
actual thing to be available in your `PATH`, e.g. together with [buf] (if you do
you might want to check out [buf-exe] as well).

> **Note** that this project is not affiliated with or endorsed by Google or the
> Protobuf team. The `-exe` suffix in the name was chosen to ensure that the
> `protoc` name stays available, just in case there ever is going to be an
> official package.

> **Warning** the redistribution process is not yet fully automated, as I am in
> the process of building the tooling. Currently only the latest `protoc`
> release is available, and it was created semi-manually with the scripts you
> currently see in the repository. The plan is to fully automate everything, and
> provide new `protoc` releases with 24 hours.

## Usage

Simply use `protoc` as the executable in whatever process abstraction you are
using, regardless of your operating system. The only requirement is that your
`PATH` is set correctly so that the `protoc` (or `protoc.exe` on Windows) is
found. For instance, you could use `pip` and a basic virtual environment:

```python
# example.py
import subprocess
subprocess.check_call(["command", "-v", "protoc"])
subprocess.check_call(["protoc", "--version"])
```

```shell
cd /tmp
python -m venv venv
source venv/bin/activate
pip install protoc-exe
command -v protoc # /tmp/venv/bin/protoc
protoc --version  # libprotoc x.y[.z]
python example.py
# /tmp/venv/bin/protoc
# libprotoc x.y[.z]
rm -fr venv/
```

> **Note** that the example uses a POSIX compliant shell, but it works on
> non-POSIX systems as well. Have a look at the GitHub Actions.

[buf]: https://buf.build/
[buf-exe]: https://github.com/fleshgrinder/python-buf-exe
[protobuf]: https://pypi.org/project/protobuf/
[protoc-wheel-0]: https://pypi.org/project/protoc-wheel-0/
[protoc-wheel]: https://pypi.org/project/protoc-wheel/
[protoc]: https://github.com/protocolbuffers/protobuf
