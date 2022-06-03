// Copyright (c) 2022 The Bitcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

// The PeersIndicator component.
// See reference design: https://bitcoindesign.github.io/Bitcoin-Core-App/assets/images/block-clock-connection-states-big.png

import QtQuick 2.15
import "../controls"

Item {
    id: root
    property int numOutboundPeers: 0
    property int maxNumOutboundPeers: 10
    property int barWidth: 4
    property int spacing: 1
    property int initialHeight: 6
    property int deltaHeight: 1

    width: bars.width
    height: bars.height

    Row {
        id: bars
        spacing: root.spacing
        Repeater {
            model: root.maxNumOutboundPeers
            delegate: Rectangle {
                required property int index
                width: root.barWidth
                height: root.initialHeight + root.deltaHeight * index
                anchors.bottom: bars.bottom
                color: Theme.color.neutral9
                opacity: index < root.numOutboundPeers ? 0.95 : 0.45
                Behavior on opacity { OpacityAnimator { duration: 100 } }
            }
        }
    }
}
