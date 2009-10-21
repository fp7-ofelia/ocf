package egeni.clearinghouse.plugin;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.Rectangle2D;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStreamWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

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
import com.jgraph.layout.organic.JGraphFastOrganicLayout;
import com.jgraph.layout.organic.JGraphOrganicLayout;
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
	private static final int INITIAL_WIDTH = 800;
	
	/**
	 * Background color
	 */
	public static final Color BG_COLOR = Color.white;

	/**
	 * URL to submit information to
	 */
	private URL submit;
	
	/**
	 * Codebase of running app or applet
	 */
	private URL codeBase;
	
	private Map<String, JGraphNode> graphNodes;
	private Map<String, JGraphLink> graphLinks;
	
	private ListenableGraph<JGraphNode, JGraphLink> graph;
	private JGraphModelAdapter<JGraphNode, JGraphLink> jgAdapter;
	private JGraph jgraph;
	
	private Boolean onComponent = false;
	
	/**
	 * Construct new panel
	 * @param codeBase: URL to use as the base for other URLs
	 * @param inputURL: URL where the XML of the graph is stored
	 */
	@SuppressWarnings({ "unchecked", "static-access" })
	public JGraphTopoPanel(URL codeBase, URL inputURL) {
		super(new BorderLayout());
		
		this.codeBase = codeBase;
		
		this.graphNodes = new HashMap<String, JGraphNode>();
		this.graphLinks = new HashMap<String, JGraphLink>();
		
		graph = new ListenableDirectedGraph<JGraphNode, JGraphLink>(JGraphLink.class);
		
		jgAdapter = new JGraphModelAdapter<JGraphNode, JGraphLink>(graph);
		
		jgraph = new JGraph(jgAdapter);
		this.adjustDisplaySettings(jgraph);

		parseInputXML(inputURL);
		
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
				if(u instanceof JGraphNode) {
					((JGraphNode)u).toggleSelected();
				} else if(u instanceof JGraphLink) {
					((JGraphLink)u).toggleSelected();
				}
			}
			
			public void mousePressed(MouseEvent e) {
				// Get Cell under Mousepointer
				int x = e.getX(), y = e.getY();
				
				System.out.println("Pressed: "+x+","+y);
				DefaultGraphCell o =
					(DefaultGraphCell)jgraph.getFirstCellForLocation(x, y);
				if(o != null) {
					onComponent = true;
				}
			}

			// TODO: Make efficient
			public void mouseReleased(MouseEvent e) {
				if(onComponent) {
					System.out.println("Released: "+e.getX()+","+e.getY());
					resizeGraph();
					onComponent = false;
				}
			}
		});
		
		/* Layout the graph nicely */
		JGraphFacade facade = new JGraphFacade(jgraph);
		facade.setDirected(true);
		JGraphOrganicLayout layout = new JGraphOrganicLayout();
		/* TODO: Figure out the best settings for these parameters */
		layout.setOptimizeNodeDistribution(true);
		layout.setOptimizeEdgeLength(true);
		layout.setNodeDistributionCostFactor(60000);
		layout.setEdgeLengthCostFactor(0.001);
		/* Make it deterministic */
		layout.setDeterministic(true);
		/* Run the layout */
		layout.run(facade);
		Map nested = facade.createNestedMap(true, true);
		jgraph.getGraphLayoutCache().edit(nested);
		
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
			System.out.println("x: " + t);
			if((t = r.getMaxY()) > y) {
				y = t;
			}
			System.out.println("y: " + t);
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
	private void parseInputXML(URL inputURL) {
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
			doc = builder.parse(this.getOrPost(inputURL, null));
		} catch (SAXException e) {
			JLabel err = new JLabel("ERROR: Could not parse XML");
			this.add(err);
			e.printStackTrace();
			return;
		} catch (IOException e) {
			JLabel err = new JLabel("ERROR: Could not read XML");
			this.add(err);
			e.printStackTrace();
			return;
		} catch (ParserConfigurationException e) {
			JLabel err = new JLabel("ERROR: XML parse misconfigured");
			this.add(err);
			e.printStackTrace();
			return;
		}
		
		try {
			submit = new URL(this.codeBase.toString()
					+ doc.getElementsByTagName("submit").item(0));
		} catch (MalformedURLException e) {
			JLabel err = new JLabel(
					"ERROR: Malformed URL: "+inputURL.toString());
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
			
			int x =
				Integer.parseInt(
						n.getElementsByTagName(
						"x").item(0).getTextContent());
				
			int y =
				Integer.parseInt(
						n.getElementsByTagName(
						"y").item(0).getTextContent());
			
			Icon img = createImageIcon(
					n.getElementsByTagName("img").item(0).getTextContent(),
					"Selected Node");

			String name = n.getElementsByTagName(
					"name").item(0).getTextContent();
			
			Boolean is_selected = n.getElementsByTagName(
					"is_selected").item(0).getTextContent().equalsIgnoreCase("True");
			
			Boolean has_error = n.getElementsByTagName(
					"has_err").item(0).getTextContent().equalsIgnoreCase("True");
			
			JGraphNode v = new JGraphNode(
					jgAdapter, graph,
					id, x, y, img, 
					name, is_selected, 
					has_error);
			graphNodes.put(id, v);
		}
		
		NodeList links = doc.getElementsByTagName("link");
		System.err.println("**** Found "+links.getLength()+" links");
		for(int i=0; i<links.getLength(); i++) {
			System.err.println("    Doing link "+i);
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
			System.err.println("    v1 Done link "+i);
			
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
				System.err.println("    Added link "+i);
			}
		}
	}

	/** Returns an ImageIcon, or null if the path was invalid. */
    protected ImageIcon createImageIcon(String path,
    		String description) {
        URL imgURL = getClass().getResource(path);
        if (imgURL != null) {
            return new ImageIcon(imgURL, description);
        } else {
            System.err.println("Couldn't find file: " + path);
            return null;
        }
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
    
    public String getParamsString(Map<String, Set<String>> map) {
		StringBuffer paramsAsString = new StringBuffer("");
		for(String k: map.keySet()) {
			Set<String> v = map.get(k);
			for(String val: v) {
				if(paramsAsString.length()>0){
					paramsAsString.append("&");
				}
				paramsAsString.append(k+"="+val);
			}
		}
		return paramsAsString.toString();
    }
    
    /**
     * Get the ids of the given key element
     * @param key: one of "node_id" or "link_id"
     * @return a String[] of all the selected ids in the topology
     */
    public String[] getIDs(String key) {
    	Set<String> s = getTopoMap().get(key);
    	String[] o = new String[s.size()];
    	o = s.toArray(o);
    	return o;
    }
    
    public String[] getNodeIDs(){
    	System.err.println("Called getNodes2");
    	return getIDs("node_id");
    }
    public String[] getLinkIDs(){
    	return getIDs("link_id");
    }

	/**
	 * Does a GET to the given URL if params is null. Otherwise,
	 * sends the params in a POST.
	 * @param url: the URL to connect to
	 * @param params: fields to send in POST. If null, then do a GET instead.
	 */
	private InputStream getOrPost(
			final URL url,
			final Map<String, Set<String>> map) 
	throws MalformedURLException, IOException {
		Boolean doOutput = map != null;
		String paramsAsString = null;
		if(doOutput) {
			paramsAsString = getParamsString(map);
		}
//		String outStr = URLEncoder.encode(paramsAsString.toString(), "UTF-8");
		
		// send parameters to server
		URLConnection con = url.openConnection();
		con.setDoOutput(doOutput);
		con.setDoInput(true);
		
		if(doOutput) {
			con.setRequestProperty("Content=length", String
					.valueOf(paramsAsString.length()));
			
			OutputStreamWriter out = new OutputStreamWriter(
					con.getOutputStream());
			out.write(paramsAsString);
			out.close();
		}
		
		return con.getInputStream();
	}
}
