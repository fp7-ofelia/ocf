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
        }
    }
    
    private void createGUI() {
        //Create and set up the content pane.
        TopoPanel newContentPane = new TopoPanel();
        newContentPane.setOpaque(true); 
        setContentPane(newContentPane);
    }
}
