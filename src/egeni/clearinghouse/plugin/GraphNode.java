import javax.swing.Icon;

/**
 * Implements a node to be drawn
 * @author jnaous
 *
 */
public class GraphNode {

	private String id;
	private int x;
	private int y;
	private Icon sel_img;
	private Icon unsel_img;
	private Icon err_img;
	private String name;
	private Boolean is_selected;
	private Boolean has_error;
	
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
		this.x = x;
		this.y = y;
		sel_img = selImg;
		unsel_img = unselImg;
		err_img = errImg;
		this.name = name;
		is_selected = isSelected;
		has_error = hasError;
	}

	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public int getX() {
		return x;
	}

	public void setX(int x) {
		this.x = x;
	}

	public int getY() {
		return y;
	}

	public void setY(int y) {
		this.y = y;
	}

	public Icon getSel_img() {
		return sel_img;
	}

	public void setSel_img(Icon selImg) {
		sel_img = selImg;
	}

	public Icon getUnsel_img() {
		return unsel_img;
	}

	public void setUnsel_img(Icon unselImg) {
		unsel_img = unselImg;
	}

	public Icon getErr_img() {
		return err_img;
	}

	public void setErr_img(Icon errImg) {
		err_img = errImg;
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
	}

	public Boolean isSelected() {
		return is_selected;
	}

	public void setIsSelected(Boolean isSelected) {
		is_selected = isSelected;
	}

	public Boolean hasError() {
		return has_error;
	}

	public void setHasError(Boolean hasError) {
		has_error = hasError;
	}
	
	
}
