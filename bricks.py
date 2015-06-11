#!/usr/bin/env python
# A game from ZetCode. Enhanced.
# http://zetcode.com/gui/pyqt4/thetetrisgame/
# I've played this in Python 2.7 and Python 3.4

from __future__ import division
import os
import sys
import platform
import random
import json
from PyQt4 import QtCore, QtGui

colorTable = [0x000000, 0xCC6666, 0x66CC66, 0x6666CC,
              0xCCCC66, 0xCC66CC, 0x66CCCC, 0xDAAA00]

dirPath = os.path.dirname(os.path.abspath(__file__))

class Bricks(QtGui.QMainWindow):
    "Main window for playing the game"
    def __init__(self):
        super(Bricks, self).__init__()
        self.initUI()

    def initUI(self):
        self.main = Main(self)
        self.setCentralWidget(self.main)

        self.setFixedSize(240, 380)
        self.center()
        self.setWindowTitle('Bricks')

        # Game menu
        new_game = QtGui.QAction('&New game', self)
        new_game.setShortcut('Ctrl+N')
        new_game.setStatusTip('New game')
        new_game.triggered.connect(self.main.bboard.new)

        save_game = QtGui.QAction('&Save game', self)
        save_game.setShortcut('Ctrl+S')
        save_game.setStatusTip('Save game')
        save_game.triggered.connect(self.main.saveGame)

        exit_game = QtGui.QAction('&Exit', self)
        exit_game.setShortcut('Ctrl+Q')
        exit_game.setStatusTip('Exit game')
        exit_game.triggered.connect(self.close)

        menubar = self.menuBar()
        game_menu = menubar.addMenu('&Game')

        game_menu.addAction(new_game)
        game_menu.addAction(save_game)
        game_menu.addSeparator()
        game_menu.addAction(exit_game)

        # Option menu
        set_level = QtGui.QAction('Set &level', self)
        set_level.setShortcut('Ctrl+L')
        set_level.setStatusTip('Set level')
        set_level.triggered.connect(self.main.bboard.setLevel)

        option_menu = menubar.addMenu('&Option')
        option_menu.addAction(set_level)

        # Help menu
        about_game = QtGui.QAction('&About', self)
        about_game.setStatusTip('About')
        about_game.triggered.connect(self.about)

        help_menu = menubar.addMenu('&Help')
        help_menu.addAction(about_game)

        # Status bar
        self.statusbar = self.statusBar()
        self.main.bboard.msg2Statusbar[str].connect(self.statusbar.showMessage)

    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Save the game?',
                                           'Save the game?',
                                           QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No,
                                           QtGui.QMessageBox.Yes)

        if reply == QtGui.QMessageBox.Yes:
            self.main.saveGame()
        event.accept()

    def center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2,
            (screen.height()-size.height())/2)

    def about(self):
        if not self.main.bboard.isPaused: self.main.bboard.pause()
        QtGui.QMessageBox.about(self, "About",
            """
            <b>A Bricks Game</b>
            <p>Base on <a href="http://zetcode.com/gui/pyqt4/">ZetCode</a>
                PyQt4 tutorial.</p>
            <p>Python {} on {}</p>
            <br/>
            """.format(platform.python_version(), platform.system())) 
        if self.main.bboard.isPaused: self.main.bboard.pause()

class Main(QtGui.QWidget):
    "Main widget in the main window contain game pad and score side bar"
    def __init__(self, parent=None):
        super(Main, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.bboard = Board(self) # This is the game pad
        self.bscore = Score(self) # This is the side bar

        grid = QtGui.QGridLayout()

        grid.addWidget(self.bboard, 1, 0, 1, 2)
        grid.addWidget(self.bscore, 1, 2, 1, 1)

        self.setLayout(grid)

        self.bboard.msg2Score[int].connect(self.bscore.set_score)
        self.bboard.msg2Next[int].connect(self.bscore.set_next)
        self.bboard.msg2Level[int].connect(self.bscore.set_level)
        self.bboard.msg2HiScore[int].connect(self.bscore.set_hiscore)

        self.bboard.loadGame()

    def saveGame(self):
        hi = int(self.bscore.hi_score.text()) // 10 # Remember this?
        score = int(self.bscore.score.text()) // 10
        board = self.bboard.board
        saved = {'board': board, 'hi': hi,
                 'score': score}
        with open(os.path.join(dirPath, 'bricks.ini'), 'w') as f:
            json.dump(saved, f)

class Score(QtGui.QWidget):
    "Score bar in the right"
    def __init__(self, parent=None):
        super(Score, self).__init__(parent)
        self.initUI()

    def initUI(self):
        score = QtGui.QLabel('Score')
        self.score = QtGui.QLabel('0')

        hi_score = QtGui.QLabel('Hi-Score')
        self.hi_score = QtGui.QLabel('0')

        next_shape = QtGui.QLabel('Next')
        self.next_shape = Next(self)

        level = QtGui.QLabel('Level')
        self.level = QtGui.QLabel('1')

        speed = QtGui.QLabel('Speed')
        self.speed = QtGui.QLabel('10')

        grid = QtGui.QGridLayout()
        grid.setSpacing(1)

        i = 0
        for w in [score, self.score, hi_score, self.hi_score,
                  next_shape, self.next_shape, level, self.level,
                  speed, self.speed]:
            grid.addWidget(w, i, 0, QtCore.Qt.AlignRight)
            i += 1

        self.setLayout(grid)

    def set_score(self, s):
        self.score.setText(str(10*s))

    def set_hiscore(self, s):
        curHi = int(self.hi_score.text())
        if curHi < 10*s:
            self.hi_score.setText(str(10*s))

    def set_next(self, s):
        self.next_shape.SHAPE = s
        self.next_shape.update()

    def set_level(self, s):
        self.level.setText(str(s))
        self.speed.setText(str(10*s))


class Next(QtGui.QFrame):
    "Next shape in the side bar"
    EDGE = 10
    SHAPE = 0

    def __init__(self, parent=None):
        super(Next, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setFixedSize(4*self.EDGE, 4*self.EDGE)
        self.show()

    def paintEvent(self, event):
        next_shape = Shape()
        next_shape.setShape(self.SHAPE)

        painter = QtGui.QPainter()
        painter.begin(self)
        for i in range(4):
            x = 1*self.EDGE - next_shape.x(i)*self.EDGE
            y = 1*self.EDGE + next_shape.y(i)*self.EDGE
            self.drawSquare(painter, y, x, self.SHAPE)
        painter.end()

    def drawSquare(self, painter, x, y, SHAPE):
        color = QtGui.QColor(colorTable[SHAPE])

        painter.fillRect(x + 1, y + 1, self.EDGE - 2, self.EDGE - 2, color)

        painter.setPen(color.light())
        painter.drawLine(x, y + self.EDGE - 1, x, y)
        painter.drawLine(x, y, x + self.EDGE - 1, y)

        painter.setPen(color.dark())
        painter.drawLine(x + 1, y + self.EDGE - 1, 
                         x + self.EDGE - 1, y + self.EDGE - 1)
        painter.drawLine(x + self.EDGE - 1, y + self.EDGE - 1, 
                         x + self.EDGE - 1, y + 1)


class LevelDlg(QtGui.QDialog):
    "Level choosing diaglog"
    def __init__(self, parent=None):
        super(LevelDlg, self).__init__(parent)
        self.initUI()

    def initUI(self):
        levelSpinBox = QtGui.QLabel('Choose level:')
        self.levelSpinBox = QtGui.QSpinBox()
        levelSpinBox.setBuddy(self.levelSpinBox)
        self.levelSpinBox.setAlignment(QtCore.Qt.AlignVCenter)
        self.levelSpinBox.setRange(1, 5)

        okBtn = QtGui.QPushButton("&OK")
        cancelBtn = QtGui.QPushButton("Cancel")

        btnLayout = QtGui.QHBoxLayout()
        btnLayout.addStretch(1)
        btnLayout.addWidget(okBtn)
        btnLayout.addWidget(cancelBtn)

        layout = QtGui.QGridLayout()
        layout.addWidget(levelSpinBox, 0, 0)
        layout.addWidget(self.levelSpinBox, 0, 1)
        layout.addLayout(btnLayout, 2, 0, 1, 3)
        self.setLayout(layout)

        okBtn.clicked.connect(self.accept)
        cancelBtn.clicked.connect(self.reject)


class Board(QtGui.QFrame):
    "Main game board in the left, where we play the brick"
    msg2Statusbar = QtCore.pyqtSignal(str)
    msg2Score = QtCore.pyqtSignal(int)
    msg2HiScore = QtCore.pyqtSignal(int)
    msg2Next = QtCore.pyqtSignal(int)
    msg2Level = QtCore.pyqtSignal(int)

    BoardWidth = 10
    BoardHeight = 22
    Speed = 500
    Level = 1

    def __init__(self, parent=None):
        super(Board, self).__init__(parent)
        self.initUI()

    def initUI(self):
        self.setStyleSheet("""
                           padding:1px;
                           border:1px solid #ccc;
                           """)

        self.timer = QtCore.QBasicTimer()
        self.isWaitingAfterLine = False

        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []
        self.shapelist = []

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.isStarted = False
        self.isPaused = False
        self.clearBoard()

    def setLevel(self):
        if not self.isPaused: self.pause()
        dialog = LevelDlg() # TODO: Should I put this here?
        dialog.levelSpinBox.setValue(self.Level)
        if dialog.exec_():
            Board.Level = dialog.levelSpinBox.value()
            self.msg2Level.emit(dialog.levelSpinBox.value())
            Board.Speed = 100*(6 - Board.Level)
            self.update()

        if self.isPaused: self.pause()

    def loadGame(self):
        self.start()
        try:
            with open(os.path.join(dirPath, 'bricks.ini'), 'r') as f:
                saved = json.load(f)

            self.start()
            self.board = saved['board']
            self.clearBoard()
            self.msg2Score.emit(saved['score'])
            self.numLinesRemoved = saved['score']
            self.msg2HiScore.emit(saved['hi'])
            self.msg2Statusbar.emit("")
        except:
            return

    def shapeAt(self, x, y):
        return self.board[(y * Board.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * Board.BoardWidth) + x] = shape

    @property
    def squareWidth(self):
        return self.contentsRect().width() // Board.BoardWidth

    @property
    def squareHeight(self):
        return self.contentsRect().height() // Board.BoardHeight

    def new(self):
        self.board = []
        self.clearBoard()
        self.msg2Statusbar.emit("")
        self.start()

    def start(self):
        if self.isPaused:
            return

        self.isStarted = True
        self.isWaitingAfterLine = False
        self.numLinesRemoved = 0
        self.clearBoard()

        self.msg2Score.emit(self.numLinesRemoved)

        self.newPiece()

        self.timer.start(Board.Speed, self)

    def pause(self):
        if not self.isStarted:
            return

        self.isPaused = not self.isPaused

        if self.isPaused:
            self.timer.stop()
            self.msg2Statusbar.emit("paused")
        else:
            self.timer.start(Board.Speed, self)
            self.msg2Statusbar.emit("")
            self.msg2Score.emit(self.numLinesRemoved)

        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        rect = self.contentsRect()

        boardTop = rect.bottom() - Board.BoardHeight * self.squareHeight

        for i in range(Board.BoardHeight):
            for j in range(Board.BoardWidth):
                shape = self.shapeAt(j, Board.BoardHeight - i - 1)

                if shape != Tetrominoe.NoShape:
                    self.drawSquare(painter,
                        rect.left() + j * self.squareWidth,
                        boardTop + i * self.squareHeight, shape)

        if self.curPiece.shape() != Tetrominoe.NoShape:
            for i in range(4):
                x = self.curX + self.curPiece.x(i)
                y = self.curY - self.curPiece.y(i)
                self.drawSquare(painter, rect.left() + x * self.squareWidth,
                    boardTop + (Board.BoardHeight - y - 1) * self.squareHeight,
                    self.curPiece.shape())

    def drawSquare(self, painter, x, y, shape):
        color = QtGui.QColor(colorTable[shape])
        painter.fillRect(x + 1, y + 1, self.squareWidth - 2,
            self.squareHeight - 2, color)

        painter.setPen(color.light())
        painter.drawLine(x, y + self.squareHeight - 1, x, y)
        painter.drawLine(x, y, x + self.squareWidth - 1, y)

        painter.setPen(color.dark())
        painter.drawLine(x + 1, y + self.squareHeight - 1,
            x + self.squareWidth - 1, y + self.squareHeight - 1)
        painter.drawLine(x + self.squareWidth - 1,
            y + self.squareHeight - 1, x + self.squareWidth - 1, y + 1)

    def keyPressEvent(self, event):
        if not self.isStarted or self.curPiece.shape() == Tetrominoe.NoShape:
            super(Board, self).keyPressEvent(event)
            return

        key = event.key()

        if key == QtCore.Qt.Key_Space:
            self.pause()
            return

        if self.isPaused:
            return

        elif key == QtCore.Qt.Key_Left:
            self.tryMove(self.curPiece, self.curX - 1, self.curY)

        elif key == QtCore.Qt.Key_Right:
            self.tryMove(self.curPiece, self.curX + 1, self.curY)

        elif key == QtCore.Qt.Key_Down:
            self.dropDown()

        elif key == QtCore.Qt.Key_Up:
            self.tryMove(self.curPiece.rotateRight(), self.curX, self.curY)
            # self.tryMove(self.curPiece.rotateLeft(), self.curX, self.curY)

        elif key == QtCore.Qt.Key_D:
            self.oneLineDown()

        else:
            super(Board, self).keyPressEvent(event)

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():

            if self.isWaitingAfterLine:
                self.isWaitingAfterLine = False
                self.newPiece()
            else:
                self.oneLineDown()

        else:
            super(Board, self).timerEvent(event)

    def clearBoard(self):
        for i in range(Board.BoardHeight * Board.BoardWidth):
            self.board.append(Tetrominoe.NoShape)

    def dropDown(self):
        newY = self.curY

        while newY > 0:

            if not self.tryMove(self.curPiece, self.curX, newY - 1):
                break

            newY -= 1

        self.pieceDropped()

    def oneLineDown(self):
        if not self.tryMove(self.curPiece, self.curX, self.curY - 1):
            self.pieceDropped()

    def pieceDropped(self):
        for i in range(4):

            x = self.curX + self.curPiece.x(i)
            y = self.curY - self.curPiece.y(i)
            self.setShapeAt(x, y, self.curPiece.shape())

        self.removeFullLines()

        if not self.isWaitingAfterLine:
            self.newPiece()

    def removeFullLines(self):
        numFullLines = 0
        rowsToRemove = []

        for i in range(Board.BoardHeight):

            n = 0
            for j in range(Board.BoardWidth):
                if not self.shapeAt(j, i) == Tetrominoe.NoShape:
                    n = n + 1

            if n == 10:
                rowsToRemove.append(i)

        rowsToRemove.reverse()

        for m in rowsToRemove:

            for k in range(m, Board.BoardHeight):
                for l in range(Board.BoardWidth):
                        self.setShapeAt(l, k, self.shapeAt(l, k + 1))

        # Score scale with level
        numFullLines = numFullLines + len(rowsToRemove) * Board.Level

        if numFullLines > 0:

            self.numLinesRemoved = self.numLinesRemoved + numFullLines
            self.msg2Score.emit(self.numLinesRemoved)

            self.isWaitingAfterLine = True
            self.curPiece.setShape(Tetrominoe.NoShape)
            self.update()

    def newPiece(self):
        while len(self.shapelist) < 2:
            curPiece = Shape()
            curPiece.setRandomShape()
            self.shapelist = [curPiece] + self.shapelist

        self.curPiece = self.shapelist.pop()

        self.msg2Next.emit(self.shapelist[0].pieceShape)

        self.curX = Board.BoardWidth // 2 - 1
        self.curY = Board.BoardHeight - 1 + self.curPiece.minY()

        if not self.tryMove(self.curPiece, self.curX, self.curY):

            self.curPiece.setShape(Tetrominoe.NoShape)
            self.timer.stop()
            self.isStarted = False
            self.msg2Statusbar.emit("Game over")
            self.msg2HiScore.emit(self.numLinesRemoved)

    def tryMove(self, newPiece, newX, newY):
        for i in range(4):

            x = newX + newPiece.x(i)
            y = newY - newPiece.y(i)

            if x < 0 or x >= Board.BoardWidth or \
                    y < 0 or y >= Board.BoardHeight:
                return False

            if self.shapeAt(x, y) != Tetrominoe.NoShape:
                return False

        self.curPiece = newPiece
        self.curX = newX
        self.curY = newY
        self.update()

        return True


class Tetrominoe(object):
    "7 brick piecies and 1 no shape code table"
    NoShape = 0
    ZShape = 1
    SShape = 2
    LineShape = 3
    TShape = 4
    SquareShape = 5
    LShape = 6
    MirroredLShape = 7


class Shape(object):
    "8 brick shapes for the game"
    coordsTable = (
        ((0, 0),     (0, 0),     (0, 0),     (0, 0)),
        ((0, -1),    (0, 0),     (-1, 0),    (-1, 1)),
        ((0, -1),    (0, 0),     (1, 0),     (1, 1)),
        ((0, -1),    (0, 0),     (0, 1),     (0, 2)),
        ((-1, 0),    (0, 0),     (1, 0),     (0, 1)),
        ((0, 0),     (1, 0),     (0, 1),     (1, 1)),
        ((-1, -1),   (0, -1),    (0, 0),     (0, 1)),
        ((1, -1),    (0, -1),    (0, 0),     (0, 1))
    )

    def __init__(self):
        self.coords = [[0,0] for i in range(4)]
        self.pieceShape = Tetrominoe.NoShape
        self.setShape(Tetrominoe.NoShape)

    def shape(self):
        return self.pieceShape

    def setShape(self, shape):
        table = Shape.coordsTable[shape]

        for i in range(4):
            for j in range(2):
                self.coords[i][j] = table[i][j]

        self.pieceShape = shape

    def setRandomShape(self):
        self.setShape(random.randint(1, 7))

    def x(self, index):
        return self.coords[index][0]

    def y(self, index):
        return self.coords[index][1]

    def setX(self, index, x):
        self.coords[index][0] = x

    def setY(self, index, y):
        self.coords[index][1] = y

    def minX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = min(m, self.coords[i][0])

        return m

    def maxX(self):
        m = self.coords[0][0]
        for i in range(4):
            m = max(m, self.coords[i][0])

        return m

    def minY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = min(m, self.coords[i][1])

        return m

    def maxY(self):
        m = self.coords[0][1]
        for i in range(4):
            m = max(m, self.coords[i][1])

        return m

    def rotateLeft(self):
        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, self.y(i))
            result.setY(i, -self.x(i))

        return result

    def rotateRight(self):
        if self.pieceShape == Tetrominoe.SquareShape:
            return self

        result = Shape()
        result.pieceShape = self.pieceShape

        for i in range(4):

            result.setX(i, -self.y(i))
            result.setY(i, self.x(i))

        return result

def main():
    app = QtGui.QApplication([])
    bricks = Bricks()
    bricks.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



