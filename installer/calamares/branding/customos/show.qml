import QtQuick 2.0
Rectangle {
    color: "#16303c"
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
        color: "#9fb3c8"
        font.pixelSize: 14
    }
}
