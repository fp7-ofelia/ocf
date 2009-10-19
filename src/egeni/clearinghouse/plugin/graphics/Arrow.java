package egeni.clearinghouse.plugin.graphics;

import java.awt.BasicStroke;
import java.awt.Graphics;
import java.awt.Graphics2D;
import java.awt.Polygon;
import java.awt.Rectangle;
import java.awt.Shape;
import java.awt.Stroke;
import java.awt.geom.AffineTransform;
import java.awt.geom.PathIterator;
import java.awt.geom.Point2D;
import java.awt.geom.Rectangle2D;

/**
 * @author Jad Naous
 *
 */
public class Arrow implements Shape {
	
	private static final long serialVersionUID = 4448513691373988978L;
	
	private static final float THICKNESS = 4;
	
	private Shape arrow;
	
	private int x0, y0, x1, y1;
	private double angle;
	
	public Arrow(Rectangle r0, Rectangle r1) {
        double x1 = r0.getCenterX();
        double y1 = r0.getCenterY();
        double x2 = r1.getCenterX();
        double y2 = r1.getCenterY();
        double theta = Math.atan2(y2 - y1, x2 - x1);
        Point2D.Double p1 = getPoint(theta, r0);
        Point2D.Double p2 = getPoint(theta+Math.PI, r1);
        
        updateShape((int)p1.x, (int)p1.y, (int)p2.x, (int)p2.y);
	}
	
	public Arrow(double x0, double y0, double x1, double y1) {
		updateShape((int)x0, (int)y0, (int)x1, (int)y1);
	}

	public Arrow(int x0, int y0, int x1, int y1) {
		updateShape(x0, y0, x1, y1);
	}

	public void updateShape(int x0, int y0, int x1, int y1) {
		double dx = x1-x0;
		double dy = y1-y0;
		
		int length = (int) Math.sqrt(Math.pow(Math.abs(dx),2) +
					Math.pow(Math.abs(dy),2));
    
		Polygon poly = new Polygon();
		poly.addPoint((int) x0,(int) y0);
		poly.addPoint((int) x0+ length,(int) y0);
		poly.addPoint((int) x0+ length-10,(int) y0-5);
		poly.addPoint((int) x0+ length,(int) y0);
		poly.addPoint((int) x0+ length-10,(int) y0+5);
		poly.addPoint((int) x0+ length,(int) y0);
		
		angle = Math.atan2(dy, dx);
		
		AffineTransform tx = AffineTransform.getRotateInstance(angle, x0, y0);

		arrow = tx.createTransformedShape((Shape)poly);
		this.x0 = x0;
		this.y0 = y0;
		this.x1 = x1;
		this.y1 = y1;
	}

    private Point2D.Double getPoint(double theta, Rectangle r) {
        double cx = r.getCenterX();
        double cy = r.getCenterY();
        double w = r.width/2;
        double h = r.height/2;
        double d = Point2D.distance(cx, cy, cx+w, cy+h);
        double x = cx + d*Math.cos(theta);
        double y = cy + d*Math.sin(theta);
        Point2D.Double p = new Point2D.Double();
        int outcode = r.outcode(x, y);
        switch(outcode) {
            case Rectangle.OUT_TOP:
                p.x = cx - h*((x-cx)/(y-cy));
                p.y = cy - h;
                break;
            case Rectangle.OUT_LEFT:
                p.x = cx - w;
                p.y = cy - w*((y-cy)/(x-cx));
                break;
            case Rectangle.OUT_BOTTOM:
                p.x = cx + h*((x-cx)/(y-cy));
                p.y = cy + h;
                break;
            case Rectangle.OUT_RIGHT:
                p.x = cx + w;
                p.y = cy + w*((y-cy)/(x-cx));
                break;
            default:
                System.out.println("Non-cardinal outcode: " + outcode);
        }
        return p;
    }
    
    public void draw(Graphics2D g) {
    	Stroke s = g.getStroke();
    	g.setStroke(new BasicStroke(THICKNESS));
    	g.draw(arrow);
    	g.setStroke(s);
    }
    
    public int getX0() {
		return x0;
	}

	public int getY0() {
		return y0;
	}

	public int getX1() {
		return x1;
	}

	public int getY1() {
		return y1;
	}
	
	public double getAngle() {
		return angle;
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
