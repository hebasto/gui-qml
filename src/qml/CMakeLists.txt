# Copyright (c) 2025-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

if(QT_KNOWN_POLICY_QTP0004)
  # Extra directories with QML files in a QML module need extra qmldir files.
  qt_policy(SET QTP0004 NEW)
endif()

set(CMAKE_AUTOMOC ON)

qt6_add_qml_module(bitcoin_qml
  URI qml
  VERSION 1.0
  STATIC
  SOURCES
    bitcoin.cpp
    imageprovider.cpp
    nodemodel.cpp
    util.cpp
  RESOURCE_PREFIX /qt/qml/
  QML_FILES
    components/BlockCounter.qml
    components/ConnectionOptions.qml
    controls/ContinueButton.qml
    controls/Header.qml
    controls/OptionButton.qml
    controls/OptionSwitch.qml
    controls/ProgressIndicator.qml
    pages/initerrormessage.qml
    pages/stub.qml
  RESOURCES
    ../qt/res/icons/bitcoin.png
)

target_compile_definitions(bitcoin_qml
  PUBLIC
    QT_NO_KEYWORDS
    QT_USE_QSTRINGBUILDER
)

target_link_libraries(bitcoin_qml
  PUBLIC
    Qt6::Widgets
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
