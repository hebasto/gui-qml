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
    property int size: 5

    implicitWidth: 64
    implicitHeight: 16

    Row {
        spacing: 6
        Repeater {
            model: root.size
            delegate: Rectangle {
                width: 8
                height: 8
                radius: width / 2
                color: Theme.color.neutral9
                opacity: (index === 0 && root.numOutboundPeers > 0) || (index + 1 <= root.size * root.numOutboundPeers / root.maxNumOutboundPeers) ? 0.95 : 0.45
                Behavior on opacity { OpacityAnimator { duration: 100 } }
            }
        }
    }
}
