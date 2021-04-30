/*

   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

 */

var svgNS = "http://www.w3.org/2000/svg";
var xlinkNS = "http://www.w3.org/1999/xlink";

/**
 * Sets the transform attribute to a scale along the x-axis
 */
function xScaleSetter(target, value){
    if(target != null){
        target.setAttributeNS(null, "transform", "scale(" + value + ", 1)");
    } else {
        System.out.println("target is null in xScaleSetter");
    }
}

/**
 * Sets the transform attribute to a scale along the y-axis
 */
function yScaleSetter(target, value){
    if(target != null){
        target.setAttributeNS(null, "transform", "scale(1, " + value + ")");
    } else {
        System.out.println("target is null in yScaleSetter");
    }
}

/**
 * Sets the transform attribute to a translate along the x-axis
 */
function xTranslateSetter(target, value){
    target.setAttributeNS(null, "transform", "translate(" + value + ", 0)");
}

/**
 * Sets the transform attribute to a translate along the y-axis
 */
function yTranslateSetter(target, value){
    target.setAttributeNS(null, "transform", "translate(0, " + value + ")");
}


function emptyElement(elt){
    var child = elt.getFirstChild();
    while(child != null){
        elt.removeChild(child);
        child = elt.getFirstChild();
    }
}

/*
 * Sets the properties in the input properties array to the values
 * in the values array on the input element
 */
function setProperties(id, properties, values){
   var elt = document.getElementById(id);
   if (elt != null){
        var newElt = elt.cloneNode(true);
        var i = 0;
        var n = properties.length;
        if (n > values.length) {
            n = values.length;
        }

        for (i=0; i<properties.length; i++){
            newElt.setAttributeNS(null, properties[i], values[i]);
        }

        elt.getParentNode().replaceChild(newElt, elt);
   } else {
        alert('No element : ' + id);
   }
}

/*
 * Set the input property on the target element
 */
function setProperty(id, property, value){
    var properties = new Array();
    properties[0] = property;
    var values = new Array();
    values[0] = value;
    setProperties(id, properties, values);
}

/**
 * Sets the requested attribute on the input element
 */
function setAttribute(id, attr, value){
    var elt = document.getElementById(id);
    if (elt != null){
        elt.setAttributeNS(null, attr, value);
    }
}

/**
 * Sets the content of a text node
 */
function setTextOrig(id, text){
    var t = document.getElementById(id);
    emptyElement(t);

    var nt = t.cloneNode(true);

    var content = document.createTextNode(text);
    nt.appendChild(content);

    var textParent = t.getParentNode();
    t.getParentNode().replaceChild(nt, t);

}

/**
 * Sets the content of a text node. Very hacky. This 
 * is a temporary work-around, until we have the 
 * bridge in order.
 */
function setText(id, text){
    var t = document.getElementById(id);
    emptyElement(t);

    var textParent = t.getParentNode();
    textParent.removeChild(t);
   
    var content = document.createTextNode(text);
    t.appendChild(content);

    textParent.appendChild(t);

}
