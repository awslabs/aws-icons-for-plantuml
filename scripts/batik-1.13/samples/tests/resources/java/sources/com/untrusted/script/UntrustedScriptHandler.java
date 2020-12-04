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
package com.untrusted.script;

import java.awt.AWTPermission;
import java.io.FilePermission;
import java.io.SerializablePermission;
import java.lang.reflect.ReflectPermission;
import java.net.NetPermission;
import java.net.SocketPermission;
import java.net.URL;
import java.security.AllPermission;
import java.security.Permission;
import java.sql.SQLPermission;
import java.util.PropertyPermission;

import javax.sound.sampled.AudioPermission;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.events.Event;
import org.w3c.dom.events.EventListener;
import org.w3c.dom.events.EventTarget;

import org.apache.batik.anim.dom.SVGOMDocument;
import org.apache.batik.bridge.ScriptHandler;
import org.apache.batik.w3c.dom.Window;

/**
 * This class implements the ScriptHandler interface and represents an 
 * example of untrusted code.
 *
 * It creates a number of Java Permissions and checks that access is denied.
 * the tests fail if the Permissions are granted.
 *
 * The only thing that the class should be allowed to make is a connection
 * back to the server that served the document containing this script.
 *
 * @author <a href="mailto:vhardy@apache.org">Vincent Hardy</a>
 * @version $Id: UntrustedScriptHandler.java 1869999 2019-11-18 21:45:45Z gadams $
 */
public class UntrustedScriptHandler implements ScriptHandler {
    public static final String svgNS = "http://www.w3.org/2000/svg";

    /**
     * Path for the file tested with FilePermission
     */
    public static final String testedPath = "build.sh";

    /**
     * Host which is used for testing
     */
    public static final String testedHost = "nagoya.apache.org:8080";

    /**
     * Table of Permissions which will be tested.
     */
    protected static Object[][] basePermissions = {
        {"AllPermission", new AllPermission()}, 
        {"FilePermission read", new FilePermission(testedPath, "read")}, 
        {"FilePermission write", new FilePermission(testedPath, "write")}, 
        {"FilePermission execute", new FilePermission(testedPath, "execute")}, 
        {"FilePermission delete", new FilePermission(testedPath, "delete")}, 
        // 1.4 {"ServicePermission", new ServicePermission("krbtgt/EXAMPLE.COM@EXAMPLE.COM", "initiate")}, 
        {"SocketPermission accept", new SocketPermission(testedHost, "accept")}, 
        {"SocketPermission connect", new SocketPermission(testedHost, "connect")}, 
        {"SocketPermission listen", new SocketPermission(testedHost, "listen")}, 
        {"SocketPermission resolve", new SocketPermission(testedHost, "resolve")}, 
        {"AudioPermission play", new AudioPermission("play")}, 
        {"AudioPermission record", new AudioPermission("record")}, 
        {"AWTPermission accessClipboard", new AWTPermission("accessClipboard")}, 
        {"AWTPermission accessEventQueue", new AWTPermission("accessEventQueue")}, 
        {"AWTPermission listenToAllAWTEvents", new AWTPermission("listenToAllAWTEvents")}, 
        {"AWTPermission showWindowWithoutWarningBanner", new AWTPermission("showWindowWithoutWarningBanner")}, 
        {"AWTPermission readDisplayPixels", new AWTPermission("readDisplayPixels")}, 
        {"AWTPermission createRobot", new AWTPermission("createRobot")}, 
        {"AWTPermission fullScreenExclusive", new AWTPermission("fullScreenExclusive")}, 
        // 1.4 {"DelegationPermission", new DelegationPermission()}, 
        // 1.4 {"LoggingPermission", new LoggingPermission("control")}, 
        {"NetPermission setDefaultAuthenticator", new NetPermission("setDefaultAuthenticator")}, 
        {"NetPermission requestPasswordAuthentication", new NetPermission("requestPasswordAuthentication")}, 
        {"NetPermission specifyStreamHandler", new NetPermission("specifyStreamHandler")}, 
        {"PropertyPermission java.home read", new PropertyPermission("java.home", "read")}, 
        {"PropertyPermission java.home write", new PropertyPermission("java.home", "write")}, 
        {"ReflectPermission", new ReflectPermission("suppressAccessChecks")}, 
        {"RuntimePermission createClassLoader", new RuntimePermission("createClassLoader")}, 
        {"RuntimePermission getClassLoader", new RuntimePermission("getClassLoader")}, 
        {"RuntimePermission setContextClassLoader", new RuntimePermission("setContextClassLoader")}, 
        {"RuntimePermission setSecurityManager", new RuntimePermission("setSecurityManager")}, 
        {"RuntimePermission createSecurityManager", new RuntimePermission("createSecurityManager")}, 
        {"RuntimePermission exitVM", new RuntimePermission("exitVM")}, 
        {"RuntimePermission shutdownHooks", new RuntimePermission("shutdownHooks")}, 
        {"RuntimePermission setFactory", new RuntimePermission("setFactory")}, 
        {"RuntimePermission setIO", new RuntimePermission("setIO")}, 
        {"RuntimePermission modifyThread", new RuntimePermission("modifyThread")}, 
        {"RuntimePermission stopThread", new RuntimePermission("stopThread")}, 
        {"RuntimePermission modifyThreadGroup", new RuntimePermission("modifyThreadGroup")}, 
        {"RuntimePermission getProtectionDomain", new RuntimePermission("getProtectionDomain")}, 
        {"RuntimePermission readFileDescriptor", new RuntimePermission("readFileDescriptor")}, 
        {"RuntimePermission writeFileDescriptor", new RuntimePermission("writeFileDescriptor")}, 
        {"RuntimePermission loadLibrary.{library name}", new RuntimePermission("loadLibrary.{library name}")}, 
        {"RuntimePermission accessClassInPackage.java.security", new RuntimePermission("accessClassInPackage.java.security")}, 
        {"RuntimePermission defineClassInPackage.java.lang", new RuntimePermission("defineClassInPackage.java.lang")}, 
        {"RuntimePermission accessDeclaredMembers", new RuntimePermission("accessDeclaredMembers")}, 
        {"RuntimePermission queuePrintJob", new RuntimePermission("queuePrintJob")}, 

        {"SecurityPermission createAccessControlContext", new SerializablePermission("createAccessControlContext")}, 
        {"SecurityPermission getDomainCombiner", new SerializablePermission("getDomainCombiner")}, 
        {"SecurityPermission getPolicy", new SerializablePermission("getPolicy")}, 
        {"SecurityPermission setPolicy", new SerializablePermission("setPolicy")}, 
        {"SecurityPermission setSystemScope", new SerializablePermission("setSystemScope")}, 
        {"SecurityPermission setIdentityPublicKey", new SerializablePermission("setIdentityPublicKey")}, 
        {"SecurityPermission setIdentityInfo", new SerializablePermission("setIdentityInfo")}, 
        {"SecurityPermission addIdentityCertificate", new SerializablePermission("addIdentityCertificate")}, 
        {"SecurityPermission removeIdentityCertificate", new SerializablePermission("removeIdentityCertificate")}, 
        {"SecurityPermission printIdentity", new SerializablePermission("printIdentity")}, 
        {"SecurityPermission getSignerPrivateKey", new SerializablePermission("getSignerPrivateKey")}, 
        {"SecurityPermission setSignerKeyPair", new SerializablePermission("setSignerKeyPair")}, 

        {"SerializablePermission enableSubclassImplementation", new SerializablePermission("enableSubclassImplementation")},
        {"SerializablePermission enableSubstitution", new SerializablePermission("enableSubstitution")},

        {"SQLPermission", new SQLPermission("setLog")}, 

        // 1.4 {"SSLPermission setHostnameVerifier", new SSLPermission("setHostnameVerifier")}
        // 1.4{"SSLPermission getSSLSessionContext", new SSLPermission("getSSLSessionContext")}
    };
    
    /**
     * Set of Permissions to test. One is added if the Document is loaded from a host
     */
    private Object[][] permissions;

    /**
     * Reference to the rectangles which show the test status
     */
    private Element[] statusRects;

    /**
     * Runs this handler.  This method is called by the SVG viewer
     * when the scripts are loaded.
     * @param doc The current document.
     * @param win An object which represents the current viewer.
     */
    public void run(final Document doc, final Window win){
        int nGrantedTmp = 0;

        //
        // If the document is loaded over the network, check that the
        // class has permission to access the server
        //
        URL docURL = ((SVGOMDocument)doc).getURLObject();
        if (docURL != null && docURL.getHost() != null && !"".equals(docURL.getHost())) {
            permissions = new Object[basePermissions.length + 3][2];
            System.arraycopy(basePermissions, 0, 
                             permissions, 3, basePermissions.length);

            String docHost = docURL.getHost();
            if (docURL.getPort() != -1) {
                docHost += ":" + docURL.getPort();
            }

            permissions[0][0] = "SocketPermission accept " + docHost;
            permissions[0][1] = new SocketPermission(docHost, "accept");
            permissions[1][0] = "SocketPermission connect " + docHost;
            permissions[1][1] = new SocketPermission(docHost, "connect");
            permissions[2][0] = "SocketPermission resolve " + docHost;
            permissions[2][1] = new SocketPermission(docHost, "resolve");
            nGrantedTmp = 3;
        } else {
            permissions = basePermissions;
        }

        // Captures the number of permissions which should be 
        // granted to this code.
        final int nGranted = nGrantedTmp;

        //
        // Build a table in the scrollable area of the document
        //
        Element securityResults = doc.getElementById("securityResults");
        statusRects = new Element[permissions.length];

        for (int i=0; i<permissions.length; i++){
            Element textElt = doc.createElementNS(svgNS, "text");
            textElt.setAttributeNS(null, "x", "55");
            textElt.setAttributeNS(null, "y", "" + (85 + i*20));
            textElt.appendChild(doc.createTextNode(permissions[i][0].toString()));
            securityResults.appendChild(textElt);

            Element rectElt = doc.createElementNS(svgNS, "rect");
            rectElt.setAttributeNS(null, "x", "50");
            rectElt.setAttributeNS(null, "y", "" + (70 + i*20));
            rectElt.setAttributeNS(null, "width", "330");
            rectElt.setAttributeNS(null, "height", "20" );
            rectElt.setAttributeNS(null, "class", "tableCell");
            securityResults.appendChild(rectElt);

            rectElt = doc.createElementNS(svgNS, "rect");
            rectElt.setAttributeNS(null, "x", "380");
            rectElt.setAttributeNS(null, "y", "" + (70 + i*20));
            rectElt.setAttributeNS(null, "width", "20");
            rectElt.setAttributeNS(null, "height", "20" );
            rectElt.setAttributeNS(null, "class", "tableCell");
            securityResults.appendChild(rectElt);

            rectElt = doc.createElementNS(svgNS, "rect");
            rectElt.setAttributeNS(null, "x", "383");
            rectElt.setAttributeNS(null, "y", "" + (73 + i*20));
            rectElt.setAttributeNS(null, "width", "14");
            rectElt.setAttributeNS(null, "height", "14" );
            rectElt.setAttributeNS(null, "class", "untested");
            securityResults.appendChild(rectElt);

            statusRects[i] = rectElt;
        }

        EventTarget testButton = (EventTarget)doc.getElementById("runTest");
        testButton.addEventListener("click", new EventListener() {
                public void handleEvent(Event evt){
                    SecurityManager sm = System.getSecurityManager();
                    int successCnt = 0;

                    if (sm == null){
                        for (int i=0; i<nGranted; i++) {
                            statusRects[i].setAttributeNS(null, "class", "passedTest");
                            successCnt++;
                        }
                        for (int i=nGranted; i<permissions.length; i++) {
                            statusRects[i].setAttributeNS(null, "class", "failedTest");
                        }
                    }
                    else {
                        for (int i=0; i<nGranted; i++) {
                            Permission p = (Permission)permissions[i][1];
                            boolean success = true;
                            try {
                                sm.checkPermission(p);
                                statusRects[i].setAttributeNS(null, "class", "passedTest");
                                successCnt++;
                            } catch (SecurityException se){
                                statusRects[i].setAttributeNS(null, "class", "failedTest");
                                System.out.println("*********************************************");
                                se.printStackTrace();
                            }
                        }

                        for (int i=nGranted; i<permissions.length; i++) {
                            Permission p = (Permission)permissions[i][1];
                            boolean success = true;
                            try {
                                sm.checkPermission(p);
                                statusRects[i].setAttributeNS(null, "class", "failedTest");
                            } catch (SecurityException se){
                                statusRects[i].setAttributeNS(null, "class", "passedTest");
                                successCnt++;
                            }
                        }

                    }

                    // Update the global status
                    Element globalStatus = doc.getElementById("globalStatus");
                    if ( successCnt == (statusRects.length) ) {
                        globalStatus.setAttributeNS(null, "class", "passedTest");
                    } else {
                        globalStatus.setAttributeNS(null, "class", "failedTest");
                    }
                    
                    String successRatioString = "Test Result: " + successCnt + " / " + statusRects.length;
                    Element successRatio = doc.getElementById("successRatio");
                    successRatio.replaceChild(doc.createTextNode(successRatioString),
                                              successRatio.getFirstChild());
                    
                }
            }, false);

        
    }

    @Override
    public void run(Document doc, org.apache.batik.bridge.Window win) {
        // TODO Auto-generated method stub

    }

}

