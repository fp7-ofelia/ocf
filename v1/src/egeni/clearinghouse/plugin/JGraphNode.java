/**
 * 
 */
package egeni.clearinghouse.plugin;

import java.awt.Color;
import java.awt.Font;
import java.awt.geom.Rectangle2D;

import javax.swing.BorderFactory;
import javax.swing.Icon;

import org.jgraph.graph.AttributeMap;
import org.jgraph.graph.DefaultGraphCell;
import org.jgraph.graph.GraphConstants;
import org.jgrapht.Graph;
import org.jgrapht.ext.JGraphModelAdapter;

/**
 * @author jnaous
 *
 */
public class JGraphNode implements SelectableItem{
	
	public static final int BORDER_THICKNESS = 0;
	
	private String id;
	private Icon img;
	private Icon trImg;
	private String name;
	private Boolean isReserved;
	private Boolean has_error;
	private JGraphModelAdapter<JGraphNode, JGraphLink> jgAdapter;
	private Boolean isSelected;
	
	/**
	 * @param jgAdapter links the graph to its view
	 * @param graph The graph to insert the node into
	 * @param id ID string of the node
	 * @param x x position of the node on the canvas in percent
	 * @param y y position of the node on the canvas in percent
	 * @param img Image to use as icon for the node
	 * @param trImg Image to use as icon for the node when not selected (transparent)
	 * @param name Name of node to display
	 * @param isSelected Whether the node is selected or not
	 * @param hasError Whether the node has an error or not
	 */
	public JGraphNode(
			JGraphModelAdapter<JGraphNode, JGraphLink> jgAdapter,
			Graph<JGraphNode,JGraphLink> graph,
			String id, double x, double y,
			Icon img, Icon trImg, String name,
			Boolean isReserved, Boolean hasError) {
		super();
		this.jgAdapter = jgAdapter;
		this.id = id;
		this.img = img;
		this.trImg = trImg;
		this.name = name;
		this.isReserved = isReserved;
		this.isSelected = isReserved;
		this.has_error = hasError;
		
		graph.addVertex(this);
		this.setDefaults(x, y);
	}
	
	@SuppressWarnings("unchecked")
	private void setDefaults(double x, double y) {
        DefaultGraphCell cell = jgAdapter.getVertexCell(this);
        AttributeMap attr = cell.getAttributes();
        GraphConstants.setAutoSize(attr, true);
        GraphConstants.setForeground(attr, Color.black);
        GraphConstants.setOpaque(attr, false);
//        GraphConstants.setIcon(attr, img);
        GraphConstants.setFont(attr, new Font("Arial", Font.PLAIN, 12));
        
        // TODO: Clean up generics once JGraph goes generic
        AttributeMap cellAttr = new AttributeMap();
        cellAttr.put(cell, attr);
        jgAdapter.edit(cellAttr, null, null, null);
        
        updateView(x, y);
	}

	@SuppressWarnings("unchecked")
	public void updateView(double x, double y) {
        DefaultGraphCell cell = jgAdapter.getVertexCell(this);
        AttributeMap attr = cell.getAttributes();
        Rectangle2D bounds = GraphConstants.getBounds(attr);

        Rectangle2D newBounds =
            new Rectangle2D.Double(
                x, y,
                bounds.getWidth(),
                bounds.getHeight());

        GraphConstants.setBounds(attr, newBounds);
    	if(hasError()) {
            GraphConstants.setBorder(attr, BorderFactory.createLineBorder(Color.red, 3));
    	} else {
    		GraphConstants.setBorder(attr, BorderFactory.createLineBorder(Color.red, 0));
    	}
    	
        if(isSelected()) {
            GraphConstants.setIcon(attr, img);
        } else {
            GraphConstants.setIcon(attr, trImg);
        }

        // TODO: Clean up generics once JGraph goes generic
        AttributeMap cellAttr = new AttributeMap();
        cellAttr.put(cell, attr);
        jgAdapter.edit(cellAttr, null, null, null);
	}
	
	public void updateView(Rectangle2D r) {
		updateView(r.getX(), r.getY());
	}

	public void setLocation(double x, double y) {
		updateView(x, y);
	}
	
	// TODO: Make efficient
	public Rectangle2D getBounds() {
		DefaultGraphCell cell = jgAdapter.getVertexCell(this);
        AttributeMap attr = cell.getAttributes();
        return GraphConstants.getBounds(attr);
	}
	
	public double getX() {
        return getBounds().getX();
	}
	
	public double getY() {
        return getBounds().getY();
	}

	@Override
	public String toString() {
		return name;
	}
	
	public Boolean equals(JGraphNode n) {
		return this.id.equals(n);
	}
	
	public String getId() {
		return id;
	}

	public Icon getImg() {
		return img;
	}

	public void setImg(Icon img) {
		this.img = img;
		updateView(getBounds());
	}

	public String getName() {
		return name;
	}

	public void setName(String name) {
		this.name = name;
		updateView(getBounds());
	}

	public Boolean isReserved() {
		return isReserved;
	}

	public void setReserved(Boolean isReserved) {
		this.isReserved = isReserved;
		updateView(getBounds());
	}

	@Override
	public Boolean isSelected() {
		return isSelected;
	}

	@Override
	public void setSelected(Boolean isSelected) {
		this.isSelected = isSelected;
		updateView(getBounds());
	}

	@Override
	public void toggleSelected() {
		setSelected(!isSelected());
	}

	public Boolean hasError() {
		return has_error;
	}

	public void setError(Boolean hasError) {
		has_error = hasError;
		updateView(getBounds());
	}
}
