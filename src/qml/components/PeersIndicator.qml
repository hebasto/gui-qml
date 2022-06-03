// Copyright (c) 2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

// The PeersIndicator component.
// See reference design: https://bitcoindesign.github.io/Bitcoin-Core-App/assets/images/block-clock-connection-states-big.png

import QtQuick 2.15
import "../controls"

Item {
    id: root
    required property int numOutboundPeers
    required property int maxNumOutboundPeers
    property real barWidth: 4
    property real barInitialHeight: 6
    property real barDeltaHeight: 1
    property alias spacing: bars.spacing

    width: bars.childrenRect.width
    height: bars.childrenRect.height

    Row {
        id: bars
        spacing: 1
        Repeater {
            model: root.maxNumOutboundPeers
            Rectangle {
                width: root.barWidth
                height: root.barInitialHeight + root.barDeltaHeight * Positioner.index
                y: -height
                color: Theme.color.neutral9
                opacity: Positioner.index < root.numOutboundPeers ? 0.95 : 0.45
                Behavior on opacity { OpacityAnimator { duration: 100 } }
            }
        }
    }
}
