package egeni.clearinghouse.plugin;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.Map;
import java.util.Set;

import javax.swing.JApplet;
import javax.swing.SwingUtilities;

public class GUIApplet extends JApplet {

	private static final long serialVersionUID = 1983426530164730695L;
	private JGraphTopoPanel topoPanel;
	private String sessionid = null;

    public void init() {
    	try {
            SwingUtilities.invokeAndWait(new Runnable() {
                public void run() {
                    createGUI();
                }
            });
        } catch (Exception e) { 
            System.err.println("createGUI didn't complete successfully");
            e.printStackTrace();
        }
    }
    
    private void createGUI() {
    	this.sessionid = getParameter("session_id");
    	String url = getParameter("inputURL");
    	String xml = getParameter("inputXML");
    	InputStream is = null;
    	if(xml != null) {
    		is = new ByteArrayInputStream(xml.getBytes());
    	} else {
    		try {
    			URL url_o = null;
    			if(url.startsWith("http://")) {
    				url_o = new URL(url);
    			} else {
    				url_o = new URL(this.getCodeBase().toString() + url);
    			}
    			try {
					is = getOrPost(url_o, null);
				} catch (IOException e) {
					// TODO Auto-generated catch block
					e.printStackTrace();
				}
    		} catch (MalformedURLException e) {
    			// TODO: ????
    			e.printStackTrace();
    		}
    	}
    	topoPanel = new JGraphTopoPanel(is);
		topoPanel.setOpaque(true);
        setContentPane(topoPanel);
    }
    
    public String getTest() {
    	return "Hello from java";
    }
    
    public JGraphTopoPanel getTopoPanel() {
    	System.err.println("Returning topo panel");
    	return topoPanel;
    }

    public String getParamsString(Map<String, Set<String>> map) {
		StringBuffer paramsAsString = new StringBuffer("");
		for(String k: map.keySet()) {
			Set<String> v = map.get(k);
			for(String val: v) {
				if(paramsAsString.length()>0){
					paramsAsString.append("&");
				}
				paramsAsString.append(k+"="+val);
			}
		}
		return paramsAsString.toString();
    }    
    
    /**
	 * Does a GET to the given URL if params is null. Otherwise,
	 * sends the params in a POST.
	 * @param url: the URL to connect to
	 * @param params: fields to send in POST. If null, then do a GET instead.
	 */
	private InputStream getOrPost(
			final URL url,
			final Map<String, Set<String>> map) 
	throws MalformedURLException, IOException {
		Boolean doOutput = map != null;
		String paramsAsString = null;
		if(doOutput) {
			paramsAsString = getParamsString(map);
		}
//		String outStr = URLEncoder.encode(paramsAsString.toString(), "UTF-8");
		
		// send parameters to server
		URLConnection con = url.openConnection();
		con.setDoOutput(doOutput);
		con.setDoInput(true);
		if(sessionid != null) {
			System.err.println("Setting cookie to "+sessionid);
			con.setRequestProperty("Cookie", "sessionid="+sessionid);
		}
		
		if(doOutput) {
			con.setRequestProperty("Content=length", String
					.valueOf(paramsAsString.length()));
			
			OutputStreamWriter out = new OutputStreamWriter(
					con.getOutputStream());
			out.write(paramsAsString);
			out.close();
		}
		
		return con.getInputStream();
	}
}
