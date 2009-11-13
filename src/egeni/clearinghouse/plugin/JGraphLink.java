package egeni.clearinghouse.plugin;

import java.awt.Color;

import org.jgraph.graph.AttributeMap;
import org.jgraph.graph.DefaultGraphCell;
import org.jgraph.graph.GraphConstants;
import org.jgrapht.Graph;
import org.jgrapht.ext.JGraphModelAdapter;
import org.jgrapht.graph.DefaultEdge;

import com.jgraph.layout.routing.JGraphParallelRouter;

public class JGraphLink extends DefaultEdge {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	public static final int WIDTH = 3;
	
	private String id;
	private Boolean is_selected;
	private Boolean is_reserved;

	private Boolean has_error;
	private JGraphModelAdapter<JGraphNode, JGraphLink> jgAdapter;

	/**
	 * @param id
	 * @param isReserved
	 * @param hasError
	 * @param jgAdapter 
	 * @param src
	 * @param dst 
	 */
	public JGraphLink(
			JGraphModelAdapter<JGraphNode, JGraphLink> jgAdapter,
			Graph<JGraphNode,JGraphLink> graph,
			JGraphNode src, JGraphNode dst, String id,
			Boolean isReserved,
			Boolean hasError) {
		super();
		this.id = id;
		is_selected = isReserved;
		is_reserved = isReserved;
		has_error = hasError;
		this.jgAdapter = jgAdapter;
		
		graph.addEdge(src, dst, this);
		
		this.setDefaults();
	}
	
	@SuppressWarnings("unchecked")
	private void setDefaults() {
        DefaultGraphCell cell = jgAdapter.getEdgeCell(this);
        AttributeMap attr = cell.getAttributes();
        GraphConstants.setLineWidth(attr, WIDTH);
        GraphConstants.setLineStyle(attr, GraphConstants.STYLE_SPLINE);
        GraphConstants.setLineEnd(attr, GraphConstants.ARROW_SIMPLE);
        GraphConstants.setRouting(attr, JGraphParallelRouter.getSharedInstance());

        // TODO: Clean up generics once JGraph goes generic
        AttributeMap cellAttr = new AttributeMap();
        cellAttr.put(cell, attr);
        jgAdapter.edit(cellAttr, null, null, null);
        
        updateView();
	}

	@SuppressWarnings("unchecked")
	public void updateView() {
        DefaultGraphCell cell = jgAdapter.getEdgeCell(this);
        AttributeMap attr = cell.getAttributes();

        if(isSelected()) {
        	if(hasError()) {
        		GraphConstants.setLineColor(attr, Color.red);
//        	} else if(isReserved()) {
//        		GraphConstants.setLineColor(attr, Color.green);
        	} else {
        		GraphConstants.setLineColor(attr, new Color(0, 0, 85));
//        		GraphConstants.setLineColor(attr, Color.blue);
        	}
        } else {
    		GraphConstants.setLineColor(attr, new Color(0, 0, 85, 255*55/100));
        }

        // TODO: Clean up generics once JGraph goes generic
        AttributeMap cellAttr = new AttributeMap();
        cellAttr.put(cell, attr);
        jgAdapter.edit(cellAttr, null, null, null);
	}

	@Override
	public String toString() {
		return null;
	}
	
	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public Boolean isSelected() {
		return is_selected;
	}

	public void setSelected(Boolean isSelected) {
		is_selected = isSelected;
		updateView();
	}

	public Boolean hasError() {
		return has_error;
	}

	public void setError(Boolean hasError) {
		has_error = hasError;
		updateView();
	}

	public void toggleSelected() {
		setSelected(!isSelected());
	}
	
	public Boolean isReserved() {
		return is_reserved;
	}

	public void setReserved(Boolean isReserved) {
		is_reserved = isReserved;
		updateView();
	}
}
