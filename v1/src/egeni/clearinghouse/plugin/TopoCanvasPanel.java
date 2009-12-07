package egeni.clearinghouse.plugin;

import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.util.Map;

import javax.swing.JPanel;

public class TopoCanvasPanel 
extends JPanel implements MouseListener {
	
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private Map<String, GraphLink> graphLinks;
	@SuppressWarnings("unused")
	private Map<String, GraphNode> graphNodes;
	
	public TopoCanvasPanel(
			Map<String, GraphLink> graphLinks,
			Map<String, GraphNode> graphNodes) {
		this.graphLinks = graphLinks;
		this.graphNodes = graphNodes;
		
		this.addMouseListener(this);
	}
	
	@Override
	public void paint(Graphics g) {
		super.paint(g);
		for(GraphLink link: graphLinks.values()) {
			link.draw((Graphics2D)g);
		}
	}

	@Override
	public void mouseClicked(MouseEvent e) {
		/* Check if any link was clicked and
		 * toggle its selected flag.
		 */
		for(GraphLink link: graphLinks.values()) {
			if(link.contains(e.getX(), e.getY())) {
				link.setSelected(!link.isSelected());
				this.repaint();
			}
		}
	}

	@Override
	public void mouseEntered(MouseEvent e) {
	}

	@Override
	public void mouseExited(MouseEvent e) {
	}

	@Override
	public void mousePressed(MouseEvent e) {
	}

	@Override
	public void mouseReleased(MouseEvent e) {
	}
}
