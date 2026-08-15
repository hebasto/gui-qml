# Copyright (c) 2026 The Bitcoin Core developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or https://opensource.org/license/mit/.

add_executable(test_bitcoin-qt
  qml/qml_tests_main.cpp
  test_unit_tests_main.cpp
)
add_windows_application_manifest(test_bitcoin-qt)

qt6_add_resources(test_bitcoin-qt qml_tests
  PREFIX /test/qml
  FILES qml/tst_mainwindow.qml
)
# See: https://bugreports.qt.io/browse/QTBUG-141858.
get_target_property(warn_flags warn_interface INTERFACE_COMPILE_OPTIONS)
if("-Wtrailing-whitespace=any" IN_LIST warn_flags)
  set_source_files_properties(${CMAKE_CURRENT_BINARY_DIR}/.qt/rcc/qrc_qml_tests.cpp PROPERTIES COMPILE_OPTIONS -Wno-trailing-whitespace)
endif()
unset(warn_flags)

target_compile_definitions(test_bitcoin-qt
  PRIVATE
    QUICK_TEST_SOURCE_DIR=":/test/qml"
)

target_link_libraries(test_bitcoin-qt
  PRIVATE
    bitcoinqml
    Qt6::QuickTest
    Qt6::Test
)

get_target_property(qt_qml_test_lib_type Qt6::Core TYPE)
if(qt_qml_test_lib_type STREQUAL "STATIC_LIBRARY")
  target_link_libraries(test_bitcoin-qt PRIVATE Qt6::qtquickcontrols2basicstyleplugin)
endif()

import_plugins(test_bitcoin-qt)
qt6_import_qml_plugins(test_bitcoin-qt)

add_test(NAME test_bitcoin-qt
  COMMAND test_bitcoin-qt --suite=unit
)

add_test(NAME test_bitcoin-qt-qml
  COMMAND test_bitcoin-qt --suite=qml -platform minimal
)

set_property(
  TEST
    test_bitcoin-qt
    test_bitcoin-qt-qml
  APPEND PROPERTY
    ENVIRONMENT_MODIFICATION
      QT_FATAL_WARNINGS=set:1
)

if(WIN32 AND VCPKG_TARGET_TRIPLET)
  set(root_path "$<SHELL_PATH:$<PATH:GET_PARENT_PATH,$<PATH:GET_PARENT_PATH,$<PATH:GET_PARENT_PATH,$<PATH:GET_PARENT_PATH,$<TARGET_PROPERTY:Qt6::QWindowsIntegrationPlugin,LOCATION_$<CONFIG>>>>>>>")
  set_property(
    TEST
      test_bitcoin-qt-qml
    APPEND PROPERTY
      ENVIRONMENT_MODIFICATION
        PATH=path_list_prepend:${root_path}/bin
        QT_PLUGIN_PATH=set:${root_path}/Qt6/plugins
        QML_IMPORT_PATH=set:${root_path}/Qt6/qml
  )
  unset(root_path)
endif()

install_binary_component(test_bitcoin-qt INTERNAL)
