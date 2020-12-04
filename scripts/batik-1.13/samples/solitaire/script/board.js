/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 * 
 *      http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
var svgns   = "http://www.w3.org/2000/svg";
var xlinkns = "http://www.w3.org/1999/xlink";

function Board(boardGroup, moveGroup, winG, helpG) {
  this.doc = boardGroup.getOwnerDocument();
  this.root = this.doc.getRootElement();
  this.helpG = (helpG)?helpG:this.doc.getElementById("help");
  this.winG  = (winG)?winG:this.doc.getElementById("win");
  this.boardGroup = boardGroup;
  this.moveGroup = moveGroup;
  this.thePiles = new Array();
  this.moves = new Array();
  this.moveIndex = 0;
  this.numMoves = 0;
  this.isWon = false;

  this.root.addEventListener("keypress", this, false);

  if (helpG) {
    var board = this;
    this.helpG.addEventListener("click", function() { board.hideHelp(); }, false);
  }
}

Board.prototype.won = function() {
  if (!this.winG) return;
  var style = this.winG.style;
  if (style.getPropertyValue("display") == "inline") {
    this.unwon();
    return;
  }
  style.setProperty("display", "inline", "");
  this.isWon = true;
};
  
Board.prototype.unwon = function() {
  if (!this.winG) return;
  if (this.winG.style.getPropertyValue("display") != "none") {
    this.winG.style.setProperty("display", "none", "");
  }
};

Board.prototype.setNotifyMoveDone = function(moveDone) {
  this.moveDone = moveDone;
};

Board.prototype.notifyMoveDone = function() {
  if (this.moveDone) {
    this.moveDone();
  }
};

Board.prototype.saveMove = function(moveinfo) {
  this.moves[this.moveIndex++] = moveinfo;
  this.numMoves = this.moveIndex;
  this.isWon = false;
};

Board.prototype.setMoveInfo = function(moveinfo) {
  if (this.moveIndex == 0) return null;
  this.moves[this.moveIndex-1] = moveinfo;
};
  
Board.prototype.getMoveInfo = function() {
  if (this.moveIndex == 0) return null;
  return this.moves[this.moveIndex-1];
};

Board.prototype.undoMove = function() {
  if (this.moveIndex == 0) return;
  if (this.isWon)          this.unwon();

  this.moveIndex--;
  var mi = this.moves[this.moveIndex];
  mi.undo();
};

Board.prototype.redoMove = function() {
  if (this.moveIndex == this.numMoves) return;

  var mi = this.moves[this.moveIndex++];
  mi.redo();

  if (this.isWon && (this.moveIndex == this.numMoves)) 
    this.won();
};

Board.prototype.handleEvent = function(evt) {
  var keycode = evt.keyCode ? evt.keyCode :
  evt.charCode ? evt.charCode :
  evt.which ? evt.which : void 0;
  var key = String.fromCharCode(keycode);
  if ((key == "z") || (key == "Z")) {
    this.undoMove();
  } else if ((key == "r") || (key == "R")) {
    this.redoMove();
  } else if (key == "?") {
    this.showHelp();
  }
};

Board.prototype.showHelp = function() {
  if (!this.helpG) return;
  var style = this.helpG.style;
  if (style.getPropertyValue("display") == "inline") {
    this.hideHelp();
    return;
  }
  style.setProperty("display", "inline", "");
  style.setProperty("pointer-events", "fill", "");
  var board = this;
}

Board.prototype.hideHelp = function() {
  if (!this.helpG) return;
  this.helpG.style.setProperty("pointer-events", "none", "");
  this.helpG.style.setProperty("display", "none", "");
}

function MultiMoveInfo(mi1, mi2) {
  this.mi1 = mi1;
  this.mi2 = mi2;
  this.undo = function() {
    this.mi2.undo();
    this.mi1.undo();
  };
  this.redo = function() {
    this.mi1.redo();
    this.mi2.redo();
  };
}

function SimpleMoveInfo(fromCards, fromPile, toCards, toPile) {
  this.fromCards = fromCards;
  this.fromPile = fromPile;
  this.toCards = toCards;
  this.toPile = toPile;
  
  this.undo = function() {
    var len = fromCards.length;
    for (var i=0; i<len; i++) {
      fromPile.moveCardTo(fromCards[i], 40, 1);
    }
  };
  this.redo = function() {
    var len = toCards.length;
    for (var i=0; i<len; i++) {
      toPile.moveCardTo(toCards[i], 40, 1);
    }
  };
}
