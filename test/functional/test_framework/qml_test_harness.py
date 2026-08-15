#!/usr/bin/env python3
# Copyright (c) 2026 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Process harness for QML functional tests."""

import os
from pathlib import Path
import secrets
import subprocess
import tempfile

from .qml_driver import QmlDriver, QmlDriverError


GUI_STARTUP_TIMEOUT = 30


class QmlTestHarness:
    """Launch the QML bitcoin-qt in an isolated datadir and connect its test bridge."""

    def __init__(self, qml_argv, tmpdir):
        self.qml_argv = list(qml_argv)
        self.tmpdir = (Path(tmpdir) / "qml").resolve()
        self.datadir = self.tmpdir / "node"
        self.config_dir = self.tmpdir / "config"
        self.cache_dir = self.tmpdir / "cache"
        self.home_dir = self.tmpdir / "home"
        self.socket_dir = None
        if os.name == "nt":
            self.socket_path = rf"\\.\pipe\bitcoin-qt-{os.getpid()}-{secrets.token_hex(16)}"
        else:
            self.socket_dir = tempfile.TemporaryDirectory(prefix="test-qml-")
            self.socket_path = Path(self.socket_dir.name) / "bridge.sock"
        self.process = None
        self.driver = None

    def start(self, extra_args=None):
        self.datadir.mkdir(parents=True)
        (self.datadir / "bitcoin.conf").write_text(
            "regtest=1\n"
            "[regtest]\n"
            "connect=0\n"
            "discover=0\n"
            "dnsseed=0\n"
            "fixedseeds=0\n"
            "listen=0\n"
            "listenonion=0\n",
            encoding="utf8",
        )

        environment = dict(os.environ)
        environment["QT_QPA_PLATFORM"] = os.getenv("QML_TEST_QPA_PLATFORM", "minimal")
        for directory in (self.config_dir, self.cache_dir, self.home_dir):
            directory.mkdir(exist_ok=True)
        environment["XDG_CONFIG_HOME"] = str(self.config_dir)
        environment["XDG_CACHE_HOME"] = str(self.cache_dir)
        environment["HOME"] = str(self.home_dir)
        arguments = self.qml_argv + [
            "-regtest",
            f"-datadir={self.datadir}",
            f"-test-automation={self.socket_path}",
            "-printtoconsole=1",
        ] + list(extra_args or [])
        self.process = subprocess.Popen(
            arguments,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            self.driver = QmlDriver(
                str(self.socket_path),
                timeout=GUI_STARTUP_TIMEOUT,
                process=self.process,
            )
        except QmlDriverError as error:
            raise QmlDriverError(f"{error}\n{self.process_output()}") from error

    def wait_for_exit(self, timeout=30):
        return self.process.wait(timeout=timeout)

    def process_output(self):
        if not self.process or self.process.poll() is None:
            return ""
        stdout, stderr = self.process.communicate()
        return "\n".join(
            output.decode("utf8", errors="replace")
            for output in (stdout, stderr)
            if output
        )

    def stop(self):
        if self.driver:
            self.driver.close()
            self.driver = None
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        if self.socket_dir:
            self.socket_dir.cleanup()
            self.socket_dir = None
