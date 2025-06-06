# Copyright (c) 2025-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

set(CMAKE_AUTOMOC ON)

qt6_add_qml_module(bitcoin_qml
  URI qml
  VERSION 1.0
  STATIC
  SOURCES
    bitcoin.cpp
  QML_FILES
    pages/stub.qml
)

target_link_libraries(bitcoin_qml
  PUBLIC
    Qt6::Quick
)

add_executable(bitcoin-qml WIN32
  main.cpp
  ../init/bitcoin-qt.cpp
)

# TODO: Switch to own resource file.
add_windows_resources(bitcoin-qml ../qt/res/bitcoin-qt-res.rc)
add_windows_application_manifest(bitcoin-qml)

target_link_libraries(bitcoin-qml
  core_interface
  bitcoin_qml
  bitcoinqt
  bitcoin_node
)

install_binary_component(bitcoin-qml)
