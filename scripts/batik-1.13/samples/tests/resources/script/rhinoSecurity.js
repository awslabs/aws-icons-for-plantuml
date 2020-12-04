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
/**
 * This ECMA Script file represents an example of untrusted code.
 *
 * It creates a number of Java Permissions and checks that access is denied.
 * the tests fail if the Permissions are granted.
 *
 * The only thing that the class should be allowed to make is a connection
 * back to the server that served the document containing this script.
 *
 * @author <a href="mailto:vhardy@apache.org">Vincent Hardy</a>
 * @version $Id: rhinoSecurity.js 1733420 2016-03-03 07:41:59Z gadams $
 */

importPackage(Packages.java.awt);
importPackage(Packages.java.io);
importPackage(Packages.java.lang.reflect);
importPackage(Packages.java.net);
importPackage(Packages.java.security);
importPackage(Packages.java.sql);
importPackage(Packages.java.util);
importPackage(Packages.javax.sound.sampled);

var svgNS = "http://www.w3.org/2000/svg";
var testedPath = "build.sh";
var testedHost = "nagoya.apache.org:8080";

var basePermissions = [
        ["AllPermission", new AllPermission()], 
        ["FilePermission read", new FilePermission(testedPath, "read")], 
        ["FilePermission write", new FilePermission(testedPath, "write")], 
        ["FilePermission execute", new FilePermission(testedPath, "execute")], 
        ["FilePermission delete", new FilePermission(testedPath, "delete")], 
        ["SocketPermission accept", new SocketPermission(testedHost, "accept")], 
        ["SocketPermission connect", new SocketPermission(testedHost, "connect")], 
        ["SocketPermission listen", new SocketPermission(testedHost, "listen")], 
        ["SocketPermission resolve", new SocketPermission(testedHost, "resolve")], 
        ["AudioPermission play", new AudioPermission("play")], 
        ["AudioPermission record", new AudioPermission("record")], 
        ["AWTPermission accessClipboard", new AWTPermission("accessClipboard")], 
        ["AWTPermission accessEventQueue", new AWTPermission("accessEventQueue")], 
        ["AWTPermission listenToAllAWTEvents", new AWTPermission("listenToAllAWTEvents")], 
        ["AWTPermission showWindowWithoutWarningBanner", new AWTPermission("showWindowWithoutWarningBanner")], 
        ["AWTPermission readDisplayPixels", new AWTPermission("readDisplayPixels")], 
        ["AWTPermission createRobot", new AWTPermission("createRobot")], 
        ["AWTPermission fullScreenExclusive", new AWTPermission("fullScreenExclusive")], 
        ["NetPermission setDefaultAuthenticator", new NetPermission("setDefaultAuthenticator")], 
        ["NetPermission requestPasswordAuthentication", new NetPermission("requestPasswordAuthentication")], 
        ["NetPermission specifyStreamHandler", new NetPermission("specifyStreamHandler")], 
        ["PropertyPermission java.home read", new PropertyPermission("java.home", "read")], 
        ["PropertyPermission java.home write", new PropertyPermission("java.home", "write")], 
        ["ReflectPermission", new ReflectPermission("suppressAccessChecks")], 
        ["RuntimePermission createClassLoader", new RuntimePermission("createClassLoader")], 
        ["RuntimePermission getClassLoader", new RuntimePermission("getClassLoader")], 
        ["RuntimePermission setContextClassLoader", new RuntimePermission("setContextClassLoader")], 
        ["RuntimePermission setSecurityManager", new RuntimePermission("setSecurityManager")], 
        ["RuntimePermission createSecurityManager", new RuntimePermission("createSecurityManager")], 
        ["RuntimePermission exitVM", new RuntimePermission("exitVM")], 
        ["RuntimePermission shutdownHooks", new RuntimePermission("shutdownHooks")], 
        ["RuntimePermission setFactory", new RuntimePermission("setFactory")], 
        ["RuntimePermission setIO", new RuntimePermission("setIO")], 
        ["RuntimePermission modifyThread", new RuntimePermission("modifyThread")], 
        ["RuntimePermission stopThread", new RuntimePermission("stopThread")], 
        ["RuntimePermission modifyThreadGroup", new RuntimePermission("modifyThreadGroup")], 
        ["RuntimePermission getProtectionDomain", new RuntimePermission("getProtectionDomain")], 
        ["RuntimePermission readFileDescriptor", new RuntimePermission("readFileDescriptor")], 
        ["RuntimePermission writeFileDescriptor", new RuntimePermission("writeFileDescriptor")], 
        ["RuntimePermission loadLibrary.{library name}", new RuntimePermission("loadLibrary.{library name}")], 
        ["RuntimePermission accessClassInPackage.java.security", new RuntimePermission("accessClassInPackage.java.security")], 
        ["RuntimePermission defineClassInPackage.java.lang", new RuntimePermission("defineClassInPackage.java.lang")], 
        ["RuntimePermission accessDeclaredMembers", new RuntimePermission("accessDeclaredMembers")], 
        ["RuntimePermission queuePrintJob", new RuntimePermission("queuePrintJob")], 
        ["SecurityPermission createAccessControlContext", new SerializablePermission("createAccessControlContext")], 
        ["SecurityPermission getDomainCombiner", new SerializablePermission("getDomainCombiner")], 
        ["SecurityPermission getPolicy", new SerializablePermission("getPolicy")], 
        ["SecurityPermission setPolicy", new SerializablePermission("setPolicy")], 
        ["SecurityPermission setSystemScope", new SerializablePermission("setSystemScope")], 
        ["SecurityPermission setIdentityPublicKey", new SerializablePermission("setIdentityPublicKey")], 
        ["SecurityPermission setIdentityInfo", new SerializablePermission("setIdentityInfo")], 
        ["SecurityPermission addIdentityCertificate", new SerializablePermission("addIdentityCertificate")], 
        ["SecurityPermission removeIdentityCertificate", new SerializablePermission("removeIdentityCertificate")], 
        ["SecurityPermission printIdentity", new SerializablePermission("printIdentity")], 
        ["SecurityPermission getSignerPrivateKey", new SerializablePermission("getSignerPrivateKey")], 
        ["SecurityPermission setSignerKeyPair", new SerializablePermission("setSignerKeyPair")], 
        ["SerializablePermission enableSubclassImplementation", new SerializablePermission("enableSubclassImplementation")],
        ["SerializablePermission enableSubstitution", new SerializablePermission("enableSubstitution")],
        ["SQLPermission", new SQLPermission("setLog")], 
    ];
    
var permissions = null;
var statusRects = null;
var nGranted = 0;
function init(){
    var docURL = document.getURLObject();
    if (docURL != null 
        && (docURL.getHost() != null)
        && !( "" == docURL.getHost())
        ) {
        permissions = new Array();

        var docHost = docURL.getHost();
        if (docURL.getPort() != -1) {
            docHost += ":" + docURL.getPort();
        }

        permissions[0] = ["SocketPermission accept " + docHost,
                          new SocketPermission(docHost, "accept")];
        permissions[1] = ["SocketPermission connect " + docHost,
                          new SocketPermission(docHost, "connect")];
        permissions[2] = ["SocketPermission resolve " + docHost,
                          new SocketPermission(docHost, "resolve")];
        // permissions.concat(basePermissions);

        for (var i=0; i<basePermissions.length; i++){
            permissions[3+i] = basePermissions[i];
        }
        nGranted = 3;
    } else {
        permissions = basePermissions;
    }

    //
    // Build a table in the scrollable area of the document
    //
    var securityResults = document.getElementById("securityResults");
    statusRects = new Array();

    for (var i=0; i<permissions.length; i++){
        var textElt = document.createElementNS(svgNS, "text");
        textElt.setAttributeNS(null, "x", "55");
        textElt.setAttributeNS(null, "y", "" + (85 + i*20));
        textElt.appendChild(document.createTextNode(permissions[i][0].toString()));
        securityResults.appendChild(textElt);

        var rectElt = document.createElementNS(svgNS, "rect");
        rectElt.setAttributeNS(null, "x", "50");
        rectElt.setAttributeNS(null, "y", "" + (70 + i*20));
        rectElt.setAttributeNS(null, "width", "330");
        rectElt.setAttributeNS(null, "height", "20" );
        rectElt.setAttributeNS(null, "class", "tableCell");
        securityResults.appendChild(rectElt);

        rectElt = document.createElementNS(svgNS, "rect");
        rectElt.setAttributeNS(null, "x", "380");
        rectElt.setAttributeNS(null, "y", "" + (70 + i*20));
        rectElt.setAttributeNS(null, "width", "20");
        rectElt.setAttributeNS(null, "height", "20" );
        rectElt.setAttributeNS(null, "class", "tableCell");
        securityResults.appendChild(rectElt);

        rectElt = document.createElementNS(svgNS, "rect");
        rectElt.setAttributeNS(null, "x", "383");
        rectElt.setAttributeNS(null, "y", "" + (73 + i*20));
        rectElt.setAttributeNS(null, "width", "14");
        rectElt.setAttributeNS(null, "height", "14" );
        rectElt.setAttributeNS(null, "class", "untested");
        securityResults.appendChild(rectElt);

        statusRects[i] = rectElt;
    }

}

init();

function runEcmascriptSecurityTest(){
    var sm = System.getSecurityManager();
    var successCnt = 0;
    if (sm == null){
        for (var i=0; i<nGranted; i++) {
            statusRects[i].setAttributeNS(null, "class", "passedTest");
            successCnt++;
        }
        for (var i=nGranted; i<permissions.length; i++) {
            statusRects[i].setAttributeNS(null, "class", "failedTest");
        }
    }
    else {
        for (var i=0; i<nGranted; i++) {
            var p = permissions[i][1];
            var success = true;
            try {
                sm.checkPermission(p);
                statusRects[i].setAttributeNS(null, "class", "passedTest");
                successCnt++;
            } catch (se){
                statusRects[i].setAttributeNS(null, "class", "failedTest");
                se.printStackTrace();
            }
        }
        for (var i=nGranted; i<permissions.length; i++) {
            var p = permissions[i][1];
            var success = true;
            try {
                sm.checkPermission(p);
                statusRects[i].setAttributeNS(null, "class", "failedTest");
            } catch (se){
                statusRects[i].setAttributeNS(null, "class", "passedTest");
                successCnt++;
            }
        }
    }

    // Update the global status
    var globalStatus = document.getElementById("globalStatus");
    if ( successCnt == (statusRects.length) ) {
        globalStatus.setAttributeNS(null, "class", "passedTest");
    } else {
        globalStatus.setAttributeNS(null, "class", "failedTest");
    }

    var successRatioString = "Test Result: " + successCnt + " / " + statusRects.length;
    var successRatio = document.getElementById("successRatio");
    successRatio.replaceChild(document.createTextNode(successRatioString),
                              successRatio.getFirstChild());
}
