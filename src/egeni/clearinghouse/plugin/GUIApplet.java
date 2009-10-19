package egeni.clearinghouse.plugin;

import java.net.MalformedURLException;
import java.net.URL;

import javax.swing.JApplet;
import javax.swing.SwingUtilities;

public class GUIApplet extends JApplet {

	private static final long serialVersionUID = 1983426530164730695L;

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
        TopoPanel newContentPane;
		try {
			newContentPane = new TopoPanel(
					this, new URL(
							this.getCodeBase().toString() + url));
//							url));
	        newContentPane.setOpaque(true); 
	        setContentPane(newContentPane);
		} catch (MalformedURLException e) {
			// TODO: ????
			e.printStackTrace();
		}
    }
}
