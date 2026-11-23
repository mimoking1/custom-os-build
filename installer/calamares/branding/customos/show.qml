import QtQuick 2.0
Rectangle {
    color: "#0a9d96"
    Text {
        anchors.centerIn: parent
        text: "أهلاً بك في @OS_NAME@\nWelcome to @OS_NAME@"
        color: "white"
        font.pixelSize: 28
        horizontalAlignment: Text.AlignHCenter
    }
    Text {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 14
        text: "Directed by Mohamed Sayed · محمد سيد"
        color: "#d8c98a"
        font.pixelSize: 14
    }
}
