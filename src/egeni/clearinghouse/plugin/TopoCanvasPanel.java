package egeni.clearinghouse.plugin;

import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.util.Vector;

import javax.swing.JPanel;

public class TopoCanvasPanel extends JPanel implements MouseListener {
	
	Vector<GraphLink> graphLinks;
	
	public TopoCanvasPanel(Vector<GraphLink> graphLinks) {
		this.graphLinks = graphLinks;
		
		this.addMouseListener(this);
	}
	
	@Override
	public void paint(Graphics g) {
		super.paint(g);
		for(GraphLink link: graphLinks) {
			link.draw((Graphics2D)g);
		}
	}

	@Override
	public void mouseClicked(MouseEvent e) {
		/* Check if any link was clicked and
		 * toggle its selected flag.
		 */
		for(GraphLink link: graphLinks) {
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
