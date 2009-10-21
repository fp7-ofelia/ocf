package egeni.clearinghouse.plugin;

import java.awt.Point;
import java.awt.event.MouseEvent;

import javax.swing.Icon;
import javax.swing.JLabel;
import javax.swing.event.MouseInputAdapter;

/**
 * Implements a node to be drawn
 * @author jnaous
 *
 */
public class GraphNode extends MouseInputAdapter {

	private String id;
	private Icon sel_img;
	private Icon unsel_img;
	private Icon err_img;
	private String name;
	private Boolean is_selected;
	private Boolean has_error;
	private JLabel label;
	private Point pe;
	
	/**
	 * @param id ID string of the node
	 * @param x x position of the node on the canvas in percent
	 * @param y y position of the node on the canvas in percent
	 * @param selImg Image to use when node is selected
	 * @param unselImg Image to use when node is not selected
	 * @param errImg Image to use when node has error
	 * @param name Name of node to display
	 * @param isSelected Whether the node is selected or not
	 * @param hasError Whether the node has an error or not
	 */
	public GraphNode(String id, int x, int y, Icon selImg, Icon unselImg,
			Icon errImg, String name, Boolean isSelected, Boolean hasError) {
		super();
		this.id = id;
		sel_img = selImg;
		unsel_img = unselImg;
		err_img = errImg;
		this.name = name;
		is_selected = isSelected;
		has_error = hasError;

		this.label = new JLabel();
		this.label.setLocation(x, y);
		this.updateLabel();
		this.label.addMouseListener(this);
		this.label.addMouseMotionListener(this);
	}
	
	/**
	 * update the text and image of the label
	 */
	private void updateLabel() {
		System.out.println("updating label");
		Icon img;
		if(this.isSelected()) {
			if(this.hasError()) {
				img = this.getErr_img();
			} else {
				img = this.getSel_img();
			}
		} else {
			img = this.getUnsel_img();
		}
		this.label.setIcon(img);
		this.label.setText(name);
		this.label.setBounds(
				this.label.getX(), this.label.getY(),
				img.getIconWidth(), img.getIconHeight());
//		this.label.repaint();
	}

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public Icon getSel_img() {
		return sel_img;
	}

	public void setSel_img(Icon selImg) {
		sel_img = selImg;
		updateLabel();
	}

	public Icon getUnsel_img() {
		return unsel_img;
	}

	public void setUnsel_img(Icon unselImg) {
		unsel_img = unselImg;
		updateLabel();
	}

	public Icon getErr_img() {
		return err_img;
	}

	public void setErr_img(Icon errImg) {
		err_img = errImg;
		updateLabel();
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
		updateLabel();
	}

	public Boolean isSelected() {
		return is_selected;
	}

	public void setSelected(Boolean isSelected) {
		is_selected = isSelected;
		updateLabel();
	}

	public Boolean hasError() {
		return has_error;
	}

	public void setError(Boolean hasError) {
		has_error = hasError;
		updateLabel();
	}

	public JLabel getLabel() {
		return label;
	}

	/**
	 * Toggle the is_selected flag.
	 * @param e
	 */
	@Override
	public void mouseClicked(MouseEvent e) {
		this.setSelected(!is_selected);
	}

	@Override
	public void mousePressed(MouseEvent e) {
		System.out.println("Pressed");
		pe = e.getPoint();
	}

	@Override
	public void mouseDragged(MouseEvent e) {
		Point pn = e.getPoint();
		System.out.printf("Dragged0 to %d,%d\n", pn.x, pn.y);
		label.setLocation(
				Math.max(0, label.getX() + pn.x - pe.x),
				Math.max(0, label.getY() + pn.y - pe.y));
	}
}
