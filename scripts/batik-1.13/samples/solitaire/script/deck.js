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
function Deck(doc, numDecks, deck, w, h) {
  this.deck = deck;
  this.cards = new Array(numDecks*52);

  var count=0;
  for (var d=0; d<numDecks; d++) {
    for (var s=0; s<4; s++) {
      for (var c=0; c<13; c++) {
        var card = new Card(doc, c+1, s+1, deck, false);
        card.setSize(w, h);
        this.cards[count++] = card;
      }
    }
  }
  return this;
}

Deck.prototype.shuffle = function() {
  var len = this.cards.length;
  for (var s=0; s<2; s++) {
    for (var x=0; x<len; x++) {
      var r = len;
      while (r >= len)
        r = Math.floor(Math.random()*(len-x));
      var c = this.cards[r];
      this.cards.splice(r, 1);
      this.cards[len-1] = c;
    }
  }
}

Deck.prototype.dealCard = function(faceup) {
  var c = this.cards.shift();
  c.flipCard(faceup);
  return c;
}
