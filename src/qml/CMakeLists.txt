# Copyright (c) 2025-present The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

if(QT_KNOWN_POLICY_QTP0004)
  # Extra directories with QML files in a QML module need extra qmldir files.
  qt_policy(SET QTP0004 NEW)
endif()

set(CMAKE_AUTOMOC ON)

set_source_files_properties(controls/Theme.qml PROPERTIES
    QT_QML_SINGLETON_TYPE TRUE
)

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
    components/AboutOptions.qml
    components/BlockCounter.qml
    components/ConnectionOptions.qml
    components/ConnectionSettings.qml
    components/DeveloperOptions.qml
    components/StorageLocations.qml
    components/StorageOptions.qml
    components/StorageSettings.qml
    controls/ContinueButton.qml
    controls/ExternalLink.qml
    controls/Header.qml
    controls/Information.qml
    controls/OptionButton.qml
    controls/OptionSwitch.qml
    controls/PageIndicator.qml
    controls/ProgressIndicator.qml
    controls/Setting.qml
    controls/TextButton.qml
    controls/Theme.qml
    controls/Wizard.qml
    pages/initerrormessage.qml
    pages/onboarding/onboarding01.qml
    pages/onboarding/onboarding01a.qml
    pages/onboarding/onboarding01b.qml
    pages/onboarding/onboarding01c.qml
    pages/onboarding/onboarding02.qml
    pages/onboarding/onboarding03.qml
    pages/onboarding/onboarding04.qml
    pages/onboarding/onboarding05.qml
    pages/onboarding/onboarding05a.qml
    pages/onboarding/onboarding05b.qml
    pages/onboarding/onboarding06.qml
    pages/onboarding/onboarding06a.qml
    pages/onboarding/onboarding06b.qml
    pages/stub.qml
  RESOURCES
    ../qt/res/icons/bitcoin.png
    res/icons/arrow-up.png
    res/icons/caret-left.png
    res/icons/caret-right.png
    res/icons/export.png
    res/icons/info.png
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
