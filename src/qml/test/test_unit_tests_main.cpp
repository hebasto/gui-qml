// Copyright (c) 2026 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#include <qml/test/qt_test_registry.h>

#include <QCoreApplication>

#include <iostream>
#include <string_view>

int RunQmlTests(int argc, char* argv[]);

namespace {
enum class TestSuite {
    UNIT,
    QML,
};

bool ParseTestSuite(int& argc, char* argv[], TestSuite& suite)
{
    constexpr std::string_view PREFIX{"--suite="};
    int output_index{1};
    bool suite_set{false};
    for (int input_index{1}; input_index < argc; ++input_index) {
        const std::string_view argument{argv[input_index]};
        if (!argument.starts_with(PREFIX)) {
            argv[output_index++] = argv[input_index];
            continue;
        }
        if (suite_set) {
            std::cerr << "The --suite option may only be specified once.\n";
            return false;
        }
        suite_set = true;
        const std::string_view value{argument.substr(PREFIX.size())};
        if (value == "unit") {
            suite = TestSuite::UNIT;
        } else if (value == "qml") {
            suite = TestSuite::QML;
        } else {
            std::cerr << "Unknown test suite: " << value << "\n";
            return false;
        }
    }
    argc = output_index;
    argv[argc] = nullptr;
    return true;
}

int RunUnitTests(int argc, char* argv[])
{
    QCoreApplication app(argc, argv);

    int status{0};
    for (const auto& test : qttestregistry::SortedEntries()) {
        status |= test.run(argc, argv);
    }
    return status;
}
} // namespace

int main(int argc, char* argv[])
{
    TestSuite suite{TestSuite::UNIT};
    if (!ParseTestSuite(argc, argv, suite)) return EXIT_FAILURE;

    switch (suite) {
    case TestSuite::UNIT:
        return RunUnitTests(argc, argv);
    case TestSuite::QML:
        return RunQmlTests(argc, argv);
    }
    return EXIT_FAILURE;
}
