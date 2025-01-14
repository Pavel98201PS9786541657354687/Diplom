QSS = '''
QMainWindow {
    background-color: #333;
    color: red;
}

/* QMenuBar --------------------------------------------------------------- */

QMenuBar {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 lightgray, stop:1 darkgray);
}
QMenuBar::item {
    spacing: 3px;           
    padding: 2px 10px;
    background-color: rgb(210,105,30);
    color: rgb(255,255,255);  
    border-radius: 5px;
}
QMenuBar::item:selected {    
    background-color: rgb(244,164,96);
}
QMenuBar::item:pressed {
    background: rgb(128,0,0);
}

/* QMenu ------------------------------------------------------------------ */

QMenu {
    font: 12pt;
    background-color: white;
    color: black;
}
QMenu::item:selected {
    color: gray;
}

/* QSplitter -------------------------------------------------------------- */

QSplitter::handle:horizontal {
    width: 2px;
    background-color : white;
}

QSplitter::handle:vertical {
    height: 2px;
    background-color : gray;
}

/*  ------------------------------------------------------------------------ */

QLabel {
/*    background-color : blue;*/
    color: #ccc;
}

QPushButton {
    min-width: 36px;
    min-height: 36px;
    border-radius: 7px;
    background: #777;
}
QPushButton:hover {
    color: white;
    background: #999;
}
QPushButton:pressed {
    background-color: #bbdefb;
    color: black;
}

Button {
    background-color: #777;
}
Button:checked {
    background-color: #ff0000;
}
'''