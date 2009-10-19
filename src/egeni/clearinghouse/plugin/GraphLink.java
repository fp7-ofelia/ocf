package egeni.clearinghouse.plugin;

import java.awt.Color;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.geom.AffineTransform;
import java.awt.geom.PathIterator;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;
import java.awt.image.AffineTransformOp;

import egeni.clearinghouse.plugin.graphics.Arrow;
import egeni.clearinghouse.plugin.graphics.BlockArrow;

public class GraphLink implements Shape {
	
	private static final int OFFSET = 6;
	
	private String id;
	private GraphNode src;
	private GraphNode dst;
	private Boolean is_selected;
	private Boolean has_error;
	
	private BlockArrow arrow;
	
	public String getId() {
		return id;
	}

	public void setId(String id) {
		this.id = id;
	}

	public GraphNode getSrc() {
		return src;
	}

	public void setSrc(GraphNode src) {
		this.src = src;
		updateArrow();
	}

	public GraphNode getDst() {
		return dst;
	}

	public void setDst(GraphNode dst) {
		this.dst = dst;
		updateArrow();
	}

	public Boolean isSelected() {
		return is_selected;
	}

	public void setSelected(Boolean isSelected) {
		is_selected = isSelected;
	}

	public Boolean hasError() {
		return has_error;
	}

	public void setError(Boolean hasError) {
		has_error = hasError;
	}

	/**
	 * @param id
	 * @param src
	 * @param dst
	 * @param isSelected
	 * @param hasError
	 */
	public GraphLink(String id, GraphNode src, GraphNode dst,
			Boolean isSelected, Boolean hasError) {
		super();
		this.id = id;
		this.src = src;
		this.dst = dst;
		is_selected = isSelected;
		has_error = hasError;
		
		updateArrow();
	}
	
	private void updateArrow() {
		Rectangle r1 = new Rectangle(src.getLabel().getBounds());
		Rectangle r2 = new Rectangle(dst.getLabel().getBounds());
		
		arrow = new BlockArrow(r1, r2, OFFSET);
	}

	public void draw(Graphics2D g) {
    	Color c = g.getColor();
    	if(isSelected()) {
    		if(hasError()) {
    			g.setColor(Color.RED);
    		} else {
    			g.setColor(Color.BLUE);
    		}
    	} else {
    		g.setColor(Color.BLACK);
    	}
		arrow.draw(g);
    	g.setColor(c);
	}

	@Override
	public boolean contains(Point2D p) {
		return arrow.contains(p);
	}

	@Override
	public boolean contains(Rectangle2D r) {
		return arrow.contains(r);
	}

	@Override
	public boolean contains(double x, double y) {
		return arrow.contains(x, y);
	}

	@Override
	public boolean contains(double x, double y, double w, double h) {
		return arrow.contains(x, y, w, h);
	}

	@Override
	public Rectangle getBounds() {
		return arrow.getBounds();
	}

	@Override
	public Rectangle2D getBounds2D() {
		return arrow.getBounds2D();
	}

	@Override
	public PathIterator getPathIterator(AffineTransform at) {
		return arrow.getPathIterator(at);
	}

	@Override
	public PathIterator getPathIterator(AffineTransform at, double flatness) {
		return arrow.getPathIterator(at, flatness);
	}

	@Override
	public boolean intersects(Rectangle2D r) {
		return arrow.intersects(r);
	}

	@Override
	public boolean intersects(double x, double y, double w, double h) {
		return arrow.intersects(x, y, w, h);
	}
}
