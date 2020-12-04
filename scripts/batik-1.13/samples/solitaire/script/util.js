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

function screenCTM(elem) {
    if (elem.getScreenCTM)
      return elem.getScreenCTM();

    // This is to handle ASV 3.0, this depends on
    // a number of bugs in the ASV implementation.
    if (elem.currentScale) {
      var scale = root.currentScale;
      var trans = root.currentTranslate;
      var ret = root.createSVGMatrix();
      ret.scale(scale);
      ret.translate(trans.x, trans.y);
      return ret;
    }

    var pMat = screenCTM(elem.parentNode);
    
    var eMat = elem.getCTM();
    if (eMat == null) return pMat;
    eMat = eMat.multiply(pMat);
    return eMat;
  }

function transformToElement(from, to) {
  if (!from.getTransformToElement) 
    return from.getTransformToElement(to);
  var m1 = screenCTM(from);
  var m2 = screenCTM(to);
  return m1.multiply(m2.inverse());
}

// Transform screen x/y to elem's coordinate system.
// returns an SVGPoint object.
function localPt(elem, x, y) {
    var mat = screenCTM(elem);
    var imat = mat.inverse();
    var cPt     = document.getRootElement().createSVGPoint();
    cPt.x = x;
    cPt.y = y;
    cPt   = cPt.matrixTransform(imat);
    return cPt;
}

function ForwardMouseDown(obj) {
  this.obj = obj;
  this.handleEvent = function(evt) {
    obj.mousedown(evt);
  }
}

function ForwardMouseMove(obj) {
  this.obj = obj;
  this.handleEvent = function(evt) {
    obj.mousemove(evt);
  }
}

function ForwardMouseUp(obj) {
  this.obj = obj;
  this.handleEvent = function(evt) {
    obj.mouseup(evt);
  }
}

