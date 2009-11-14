package egeni.clearinghouse.plugin;

import java.awt.AlphaComposite;
import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.KeyEvent;
import java.awt.event.KeyListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.Rectangle2D;
import java.awt.image.BufferedImage;
import java.awt.image.FilteredImageSource;
import java.awt.image.ImageFilter;
import java.awt.image.RGBImageFilter;
import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Map;
import java.util.Random;
import java.util.Set;
import java.util.Vector;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JApplet;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;

import org.jgraph.JGraph;
import org.jgraph.event.GraphLayoutCacheEvent;
import org.jgraph.event.GraphLayoutCacheListener;
import org.jgraph.event.GraphSelectionEvent;
import org.jgraph.event.GraphSelectionListener;
import org.jgraph.graph.AttributeMap;
import org.jgraph.graph.DefaultGraphCell;
import org.jgraph.graph.GraphConstants;
import org.jgraph.util.ParallelEdgeRouter;
import org.jgrapht.Graph;
import org.jgrapht.ListenableGraph;
import org.jgrapht.ext.JGraphModelAdapter;
import org.jgrapht.graph.DefaultEdge;
import org.jgrapht.graph.ListenableDirectedGraph;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.jgraph.layout.JGraphFacade;
import com.jgraph.layout.JGraphLayout;
import com.jgraph.layout.graph.JGraphSpringLayout;
import com.jgraph.layout.organic.JGraphFastOrganicLayout;
import com.jgraph.layout.organic.JGraphOrganicLayout;
import com.jgraph.layout.organic.JGraphSelfOrganizingOrganicLayout;
import com.jgraph.layout.routing.JGraphParallelRouter;
import com.jgraph.layout.tree.JGraphRadialTreeLayout;

@SuppressWarnings("unused")
public class JGraphTopoPanel extends JPanel {

	private static final long serialVersionUID = 1L;

	/**
	 * Initial preferred height of the canvas
	 */
	private static final int INITIAL_HEIGHT = 600;
	/**
	 * Initial preferred width of the canvas
	 */
	private static final int INITIAL_WIDTH = 740;
	
	/**
	 * Max Icon width
	 */
	public static final int MAX_ICON_WIDTH = 85;
	
	/**
	 * Max Icon height
	 */
	public static final int MAX_ICON_HEIGHT = 64;

	/**
	 * Background color
	 */
	public static final Color BG_COLOR = Color.white;

	private Map<String, JGraphNode> graphNodes;
	private Map<String, JGraphLink> graphLinks;
	
	private Map<String, Image> images;
	private Map<Image, Image> transparentImages;
	
	private ListenableGraph<JGraphNode, JGraphLink> graph;
	private JGraphModelAdapter<JGraphNode, JGraphLink> jgAdapter;
	private JGraph jgraph;
	
	private Boolean onComponent = false;
	
	/**
	 * Construct new panel
	 * @param inputXML: InputStream whence to read the xml
	 */
	@SuppressWarnings({ "unchecked", "static-access" })
	public JGraphTopoPanel(InputStream inputXML) {
		super(new BorderLayout());
		
		this.graphNodes = new HashMap<String, JGraphNode>();
		this.graphLinks = new HashMap<String, JGraphLink>();
		this.images = new HashMap<String, Image>();
		this.transparentImages = new HashMap<Image, Image>();
		
		graph = new ListenableDirectedGraph<JGraphNode, JGraphLink>(JGraphLink.class);
		
		jgAdapter = new JGraphModelAdapter<JGraphNode, JGraphLink>(graph);
		
		jgraph = new JGraph(jgAdapter);
		this.adjustDisplaySettings(jgraph);
		jgraph.addGraphSelectionListener(new GraphSelectionListener() {
			@Override
			public void valueChanged(GraphSelectionEvent e) {
				Object[] o = jgraph.getSelectionCells();
				if(o == null) return;
				/* if any cell is unselected then select all */
				Boolean doSelect = false;
				LinkedList<SelectableItem> items = new LinkedList<SelectableItem>();
				/* check to see if anything is not selected */
				for(Object c: o) {
					DefaultGraphCell cell = (DefaultGraphCell) c;
					Object u = cell.getUserObject();
					if(u instanceof SelectableItem) {
						items.add((SelectableItem)u);
						if(!((SelectableItem)u).isSelected()) {
							doSelect = true;
						}
					}
				}
				/* set the selection status */
				for(SelectableItem u: items) {
					u.setSelected(doSelect);
				}
			}
		});

		parseInputXML(inputXML);
		
		JScrollPane sPane = new JScrollPane(jgraph);
		this.add(sPane, BorderLayout.CENTER);
		
		jgraph.addMouseListener(new MouseAdapter() {
			public void mouseClicked(MouseEvent e) {
				// Get Cell under Mousepointer
				int x = e.getX(), y = e.getY();
				DefaultGraphCell o =
					(DefaultGraphCell)jgraph.getFirstCellForLocation(x, y);
				if(o == null) return;
				Object u = o.getUserObject();
				if(u instanceof SelectableItem) {
					((SelectableItem)u).toggleSelected();
				}
			}
			
			public void mousePressed(MouseEvent e) {
				// Get Cell under Mousepointer
				int x = e.getX(), y = e.getY();
				
//				System.out.println("Pressed: "+x+","+y);
				DefaultGraphCell o =
					(DefaultGraphCell)jgraph.getFirstCellForLocation(x, y);
				if(o != null) {
					onComponent = true;
				}
			}

			// TODO: Make efficient
			public void mouseReleased(MouseEvent e) {
				if(onComponent) {
//					System.out.println("Released: "+e.getX()+","+e.getY());
					resizeGraph();
					onComponent = false;
				}
			}
		});

		/* Get the nodes that need to be laid out */
		Random rand = new Random();
		Set<JGraphNode> vset = new HashSet<JGraphNode>();
		for(JGraphNode n: graphNodes.values()) {
			if(n.getX() < 0 || n.getY() < 0) {
				n.setLocation(rand.nextDouble()*INITIAL_WIDTH*0.5,
						rand.nextDouble()*INITIAL_HEIGHT*0.5);
//				System.err.println("Adding for layout node "+n.getId());
				vset.add(n);
			}
		}
		/* Layout the graph nicely */
//		System.err.println("Doing layout");
		JGraphFacade facade = new JGraphFacade(jgraph);
		facade.setDirected(true);
		facade.setVerticesFilter(vset);
		JGraphOrganicLayout layout = new JGraphOrganicLayout();
		/* TODO: Figure out the best settings for these parameters */
		layout.setOptimizeNodeDistribution(true);
		layout.setOptimizeEdgeLength(true);
		layout.setNodeDistributionCostFactor(600000);
		layout.setEdgeLengthCostFactor(0.001);
		/* Run the layout */
		layout.run(facade);
		Map nested = facade.createNestedMap(true, true);
		jgraph.getGraphLayoutCache().edit(nested);
//		System.err.println("Layout done");
		
		JGraphParallelRouter.getSharedInstance().setEdgeDeparture(5);
		JGraphParallelRouter.getSharedInstance().setEdgeSeparation(8);
		
		resizeGraph();
	}

	private void resizeGraph() {
		double x = 0;
		double y = 0;
		double t;
		for(JGraphNode n: graphNodes.values()) {
			Rectangle2D r = n.getBounds();
			if((t = r.getMaxX()) > x) {
				x = t;
			}
//			System.out.println("x: " + t);
			if((t = r.getMaxY()) > y) {
				y = t;
			}
//			System.out.println("y: " + t);
			jgraph.setPreferredSize(new Dimension((int) x, (int) y));
		}
	}

	/**
	 * set default display setting for the given graph
	 * @param jg
	 */
    private void adjustDisplaySettings(JGraph jg)
    {
        jg.setPreferredSize(new Dimension(INITIAL_WIDTH, INITIAL_HEIGHT));
        jg.setBackground(BG_COLOR);
        jg.setAntiAliased(true);
        jg.setEditable(false);
        jg.setBendable(false);
        jg.setCloneable(false);
        jg.setConnectable(false);
        jg.setDisconnectable(false);
        jg.setDropEnabled(false);
        jg.setSizeable(false);
    }
    
    /**
     * Read XML from the inputURL and parse it into a set of nodes and links
     * @param inputURL
     */
	private void parseInputXML(InputStream is) {
		Document doc = null;
		try {
//			SchemaFactory sfactory = SchemaFactory.newInstance(
//					XMLConstants.W3C_XML_SCHEMA_NS_URI);
//			Schema schema = sfactory.newSchema(
//					new URL(applet.getCodeBase().toString() 
//							+ "plugin.xsd"));
			
			DocumentBuilderFactory factory = 
				DocumentBuilderFactory.newInstance();
//			factory.setValidating(true);
//			factory.setSchema(schema);
			
			DocumentBuilder builder = factory.newDocumentBuilder();
			doc = builder.parse(is);
		} catch (SAXException e) {
			JLabel err = new JLabel("ERROR: Could not parse XML");
			this.add(err);
			e.printStackTrace();
			return;
		} catch (ParserConfigurationException e) {
			JLabel err = new JLabel("ERROR: XML parse misconfigured");
			this.add(err);
			e.printStackTrace();
			return;
		} catch (IOException e) {
			JLabel err = new JLabel("ERROR: Could not read XML");
			this.add(err);
			e.printStackTrace();
			return;
		}
		
		NodeList nodes = doc.getElementsByTagName("node");
		System.err.println("**** Found "+nodes.getLength()+" nodes");
		for(int i=0; i<nodes.getLength(); i++) {
			Element n = (Element) nodes.item(i);
			
			String id = 
				n.getElementsByTagName(
				"id").item(0).getTextContent();
			
			double x =
				Double.parseDouble(
						n.getElementsByTagName(
						"x").item(0).getTextContent());
				
			double y =
				Double.parseDouble(
						n.getElementsByTagName(
						"y").item(0).getTextContent());
			
			ImageIcon img = createImageIcon(
					n.getElementsByTagName("img").item(0).getTextContent(),
					"Selected Node");
			ImageIcon trImg = createTransparentImageIcon(img.getImage(), "Unselected Node");

			String name = n.getElementsByTagName(
					"name").item(0).getTextContent();
			
			Boolean is_selected = n.getElementsByTagName(
					"is_selected").item(0).getTextContent().equalsIgnoreCase("True");
			
			Boolean has_error = n.getElementsByTagName(
					"has_err").item(0).getTextContent().equalsIgnoreCase("True");
			
			JGraphNode v = new JGraphNode(
					jgAdapter, graph,
					id, x, y, img, trImg,
					name, is_selected, 
					has_error);
			graphNodes.put(id, v);
		}
		
		NodeList links = doc.getElementsByTagName("link");
		System.err.println("**** Found "+links.getLength()+" links");
		for(int i=0; i<links.getLength(); i++) {
//			System.err.println("    Doing link "+i);
			Element n = (Element) links.item(i);
			
			String id = 
				n.getElementsByTagName(
						"id").item(0).getTextContent();
			
			String src_id = n.getElementsByTagName(
					"src").item(0).getTextContent();
			
			String dst_id = n.getElementsByTagName(
					"dst").item(0).getTextContent();
			
			Boolean is_selected = n.getElementsByTagName(
					"is_selected").item(0).getTextContent(
							).equalsIgnoreCase("True");
			
			Boolean has_error = n.getElementsByTagName(
					"has_err").item(0).getTextContent(
							).equalsIgnoreCase("True");
//			System.err.println("    v1 Done link "+i);
			
			if(!graphNodes.containsKey(src_id)) {
				System.err.printf("Link %d missing src id %s\n", i, src_id);
			} else if(!graphNodes.containsKey(dst_id)) {
				System.err.printf("Link %d missing dst id %s\n", i, dst_id);
			} else {
				JGraphLink l = new JGraphLink(
						jgAdapter, graph,
						graphNodes.get(src_id),
						graphNodes.get(dst_id),						
						id, is_selected, has_error);
				graph.addEdge(
						graphNodes.get(src_id),
						graphNodes.get(dst_id),
						l);
				graphLinks.put(id, l);
//				System.err.println("    Added link "+i);
			}
		}
	}

	/**
	 * Gets the image specified by the path, scales it, and stores 
	 * it if not already done so before. Then returns an ImageIcon
	 * using that image.
	 */
    protected ImageIcon createImageIcon(String path,
    		String description) {
    	
    	/* If we already have loaded and scaled this image then use it */
    	if(images.containsKey(path)) {
    		return new ImageIcon(images.get(path), description);
    	}
    	
        URL imgURL = getClass().getResource(path);
        ImageIcon imgIcon = null;
        if (imgURL != null) {
            imgIcon = new ImageIcon(imgURL, description);
        } else {
            System.err.println("Couldn't find file: " + path);
            imgIcon = new ImageIcon(path);
        }
        if(imgIcon != null) {
        	int h = -1;
        	int w = -1;
        	/* get the largest ratio */
        	if(imgIcon.getIconHeight() * 1.0 / MAX_ICON_HEIGHT
        			> imgIcon.getIconWidth() * 1.0 / MAX_ICON_WIDTH) {
        		/* scale by height */
        		h = Math.min(MAX_ICON_HEIGHT, imgIcon.getIconHeight());
        	} else {
        		/* scale by width */
        		w = Math.min(MAX_ICON_WIDTH, imgIcon.getIconWidth());        		
        	}
        	Image scaledImg = imgIcon.getImage().getScaledInstance(w, h, Image.SCALE_SMOOTH);
        	images.put(path, scaledImg);
        	return new ImageIcon(scaledImg, description);
        } else {
        	return new ImageIcon((Image)null, description);
        }
    }
    
    protected ImageIcon createTransparentImageIcon(Image img, String description) {
    	if(this.transparentImages.containsKey(img)) {
    		return new ImageIcon(this.transparentImages.get(img));
    	}
    	
    	ImageFilter grayFilter = new RGBImageFilter() {
    		
    		Boolean canFilterIndexColorModel = true;
    		
			@Override
			public int filterRGB(int x, int y, int rgb) {
				int a = rgb & 0xff000000;
				int r = (rgb >> 16) & 0xff;
				int g = (rgb >> 8) & 0xff;
				int b = rgb & 0xff;
				r = (r+255)/2;
				g = (g+255)/2;
				b = (b+255)/2;
				return a | (r << 16) | (g << 8) | b;
			}
		};
		
		Image aimg = createImage(new FilteredImageSource(img.getSource(), grayFilter));
    	
//    	BufferedImageBuilder bib = new BufferedImageBuilder();
//    	BufferedImage bimg = bib.bufferImage(img);
//
//    	// Create the image using the
//		BufferedImage aimg = new BufferedImage(bimg.getWidth(), bimg
//				.getHeight(), BufferedImage.TRANSLUCENT);
//		// Get the images graphics
//		Graphics2D g = aimg.createGraphics();
//		// Set the Graphics composite to Alpha
//		g.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER,
//				(float)0.5));
//		// Draw the LOADED img into the prepared reciver image
//		g.drawImage(bimg, null, 0, 0);
//		// let go of all system resources in this Graphics
//		g.dispose();

		// Return the image
		this.transparentImages.put(img, aimg);
		return new ImageIcon(aimg, description);
	}

    /**
     * Returns a Map mapping:
     *    link_id-> set of selected link id's in the topology
     *    node_id-> set of selected node id's in the topology
     * @return
     */
    public Map<String, Set<String>> getTopoMap() {
		Map<String,Set<String>> map = 
			new HashMap<String, Set<String>>();
		
		HashSet<String> v = new HashSet<String>();
		for(JGraphNode n: this.graph.vertexSet()) {
			if(n.isSelected()) {
				v.add(n.getId());
			}
		}
		map.put("node_id", v);
		
		v = new HashSet<String>();
		for(JGraphLink l: this.graphLinks.values()) {
			if(l.isSelected()) {
				v.add(l.getId());
			}
		}
		map.put("link_id", v);
		
		return map;
    }
    
	public JGraphNode[] getGraphNodes() {
		JGraphNode[] a = new JGraphNode[graphNodes.size()];
		a = graphNodes.values().toArray(a);
		return a;
	}

	public JGraphLink[] getGraphLinks() {
		JGraphLink[] a = new JGraphLink[graphLinks.size()];
		return graphLinks.values().toArray(a);
	}
}
