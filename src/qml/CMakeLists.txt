# Copyright (c) 2026 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

include(ImportQtPlugins)

set(CMAKE_AUTOMOC ON)

qt6_add_resources(BITCOIN_QML_QRC bitcoin_qml.qrc)
# See: https://bugreports.qt.io/browse/QTBUG-141858.
get_target_property(warn_flags warn_interface INTERFACE_COMPILE_OPTIONS)
if("-Wtrailing-whitespace=any" IN_LIST warn_flags)
  set_source_files_properties(${BITCOIN_QML_QRC} PROPERTIES COMPILE_OPTIONS -Wno-trailing-whitespace)
endif()
unset(warn_flags)

add_library(bitcoinqml STATIC
  bitcoin.cpp
  bitcoin.h
  bitcoinqmlapplication.cpp
  bitcoinqmlapplication.h
  initexecutor.cpp
  initexecutor.h
  models/nodemodel.cpp
  models/nodemodel.h
  ${BITCOIN_QML_QRC}
)

target_compile_definitions(bitcoinqml
  PUBLIC
    QT_NO_KEYWORDS
    QT_NO_CONTEXTLESS_CONNECT
    QT_USE_QSTRINGBUILDER
)

target_sources(bitcoinqml
  PRIVATE
    test/testbridge.cpp
    test/testbridge.h
)

target_link_libraries(bitcoinqml
  PRIVATE
    bitcoin_node
  PUBLIC
    Qt6::Qml
    Qt6::Quick
    Qt6::QuickControls2
    Qt6::Network
)

add_executable(bitcoin-qt WIN32
  main.cpp
  ../qt/res/bitcoin-qt-res.rc
  ../init/bitcoin-qt.cpp
)
add_windows_application_manifest(bitcoin-qt)

target_compile_definitions(bitcoin-qt
  PRIVATE
    BITCOIN_GUI_EXECUTABLE_NAME="bitcoin-qt"
)

target_link_libraries(bitcoin-qt
  PRIVATE
    core_interface
    bitcoinqml
    bitcoin_node
    $<TARGET_NAME_IF_EXISTS:bitcoin_wallet>
)

qt6_import_qml_plugins(bitcoin-qt)
import_plugins(bitcoin-qt)
install_binary_component(bitcoin-qt HAS_MANPAGE)

if(ENABLE_IPC)
  add_executable(bitcoin-gui WIN32
    main.cpp
    ../init/bitcoin-gui.cpp
  )
  target_link_libraries(bitcoin-gui
    PRIVATE
      core_interface
      bitcoinqml
      bitcoin_node
      bitcoin_ipc
      $<TARGET_NAME_IF_EXISTS:bitcoin_wallet>
  )
  qt6_import_qml_plugins(bitcoin-gui)
  import_plugins(bitcoin-gui)
  install_binary_component(bitcoin-gui INTERNAL)
endif()

if(BUILD_GUI_TESTS)
  add_subdirectory(test)
endif()
