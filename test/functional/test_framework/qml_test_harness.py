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
import unittest
from unittest.mock import Mock

from .qml_driver import QmlDriver, QmlDriverError


GUI_STARTUP_TIMEOUT = 30


class QmlTestHarness:
    """Launch a QML GUI in an isolated datadir and connect its test bridge."""

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
        try:
            if self.process and self.process.poll() is None:
                if self.driver:
                    try:
                        self.driver.close_window()
                        self.process.wait(timeout=10)
                    except (QmlDriverError, OSError, subprocess.TimeoutExpired):
                        pass
                if self.process.poll() is None:
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                        self.process.wait(timeout=10)
        finally:
            if self.driver:
                self.driver.close()
                self.driver = None
            if self.socket_dir:
                self.socket_dir.cleanup()
                self.socket_dir = None


class TestFrameworkQmlTestHarness(unittest.TestCase):
    def setUp(self):
        self.harness = QmlTestHarness([], tempfile.gettempdir())
        if self.harness.socket_dir:
            self.addCleanup(self.harness.socket_dir.cleanup)
        self.driver = self.harness.driver = Mock(spec=QmlDriver)
        self.process = self.harness.process = Mock(spec=subprocess.Popen)

    def test_stop_requests_graceful_shutdown(self):
        self.process.poll.side_effect = [None, 0]

        def wait(*, timeout):
            self.assertEqual(timeout, 10)
            self.driver.close_window.assert_called_once_with()
            self.driver.close.assert_not_called()
            return 0

        self.process.wait.side_effect = wait
        self.harness.stop()

        self.process.wait.assert_called_once_with(timeout=10)
        self.process.terminate.assert_not_called()
        self.process.kill.assert_not_called()
        self.driver.close.assert_called_once_with()
        self.assertIsNone(self.harness.driver)
        self.assertIsNone(self.harness.socket_dir)

    def test_stop_terminates_when_bridge_fails(self):
        self.process.poll.return_value = None
        self.driver.close_window.side_effect = QmlDriverError("Bridge disconnected")

        self.harness.stop()

        self.driver.close_window.assert_called_once_with()
        self.process.terminate.assert_called_once_with()
        self.process.wait.assert_called_once_with(timeout=10)
        self.process.kill.assert_not_called()
        self.driver.close.assert_called_once_with()

    def test_stop_terminates_after_graceful_timeout(self):
        self.process.poll.return_value = None
        self.process.wait.side_effect = [subprocess.TimeoutExpired("bitcoin-qt", 10), 0]

        self.harness.stop()

        self.driver.close_window.assert_called_once_with()
        self.process.terminate.assert_called_once_with()
        self.process.kill.assert_not_called()
        self.assertEqual(self.process.wait.call_count, 2)
        self.driver.close.assert_called_once_with()

    def test_stop_kills_after_terminate_timeout(self):
        self.harness.driver = None
        self.process.poll.return_value = None
        self.process.wait.side_effect = [subprocess.TimeoutExpired("bitcoin-qt", 10), 0]

        self.harness.stop()

        self.process.terminate.assert_called_once_with()
        self.process.kill.assert_called_once_with()
        self.assertEqual(self.process.wait.call_count, 2)
        for args in self.process.wait.call_args_list:
            self.assertEqual(args.kwargs, {"timeout": 10})
        self.assertIsNone(self.harness.socket_dir)

    def test_stop_after_process_exit_is_repeatable(self):
        self.process.poll.return_value = 0

        self.harness.stop()
        self.harness.stop()

        self.driver.close_window.assert_not_called()
        self.driver.close.assert_called_once_with()
        self.process.terminate.assert_not_called()
        self.process.kill.assert_not_called()
        self.process.wait.assert_not_called()

    def test_stop_before_start(self):
        self.harness.driver = None
        self.harness.process = None

        self.harness.stop()

        self.assertIsNone(self.harness.socket_dir)
