// Copyright (c) 2023 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

import QtQuick 2.15
import QtQuick.Controls 2.15

SwipeView {
    id: swipeView
    property bool finished: false
    interactive: false

    OnboardingCover {}
    OnboardingStrengthen {}
    OnboardingBlockclock {}
    OnboardingStorageLocation {}
    OnboardingStorageAmount {}
    OnboardingConnection {}
}
