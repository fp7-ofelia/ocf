package egeni.clearinghouse.plugin;

import java.net.MalformedURLException;
import java.net.URL;

import javax.swing.JApplet;
import javax.swing.SwingUtilities;

public class GUIApplet extends JApplet {

	private static final long serialVersionUID = 1983426530164730695L;
	private JGraphTopoPanel topoPanel;

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
    	String url = getParameter("inputURL");
		try {
			if(url.startsWith("http://")) {
				topoPanel = new JGraphTopoPanel(
						this.getCodeBase(), new URL(url));
			} else {
				topoPanel = new JGraphTopoPanel(
						this.getCodeBase(), new URL(
								this.getCodeBase().toString() + url));
			}
			topoPanel.setOpaque(true);
	        setContentPane(topoPanel);
		} catch (MalformedURLException e) {
			// TODO: ????
			e.printStackTrace();
		}
    }
    
    public String getTest() {
    	return "Hello from java";
    }
    
    public JGraphTopoPanel getTopoPanel() {
    	return topoPanel;
    }
    
}
