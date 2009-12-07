package egeni.clearinghouse.plugin;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
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

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

@SuppressWarnings("unused")
public class TopoPanel extends JPanel implements ActionListener {

	private static final long serialVersionUID = -8517569564217332387L;

	private static final String RESET_ACTION = "RESET";
	private static final String RESERVE_ACTION = "RESERVE";
	private JPanel canvasPanel;
	private Map<String, GraphNode> graphNodes;
	private Map<String, GraphLink> graphLinks;
	private URL submit;
	private JApplet applet;
	
	public TopoPanel(JApplet applet, URL inputURL) {
		super(new BorderLayout());
		
		this.applet = applet;
		
		this.graphNodes = new HashMap<String, GraphNode>();
		this.graphLinks = new HashMap<String, GraphLink>();
		
		canvasPanel = new TopoCanvasPanel(graphLinks, graphNodes);
		canvasPanel.setBackground(Color.white);
		JScrollPane sPane = new JScrollPane(canvasPanel);
		this.add(sPane, BorderLayout.CENTER);
		canvasPanel.setPreferredSize(new Dimension(400, 400));

		parseInputXML(inputURL);
		drawTopo();
		
//		JPanel bottomPanel = new JPanel();
//		
//		JButton reserveButton = new JButton("Reserve");
//		JButton resetButton = new JButton("Reset");
//		
//		bottomPanel.add(reserveButton);
//		bottomPanel.add(resetButton);
//		this.add(bottomPanel, BorderLayout.SOUTH);
//		
//		reserveButton.setActionCommand(RESERVE_ACTION);
//		resetButton.setActionCommand(RESET_ACTION);
//		
//		reserveButton.addActionListener(this);
//		resetButton.addActionListener(this);
	}

	/**
	 * Add components of the topology into the canvas
	 */
    private void drawTopo() {
		this.canvasPanel.setLayout(null);
		
		/* Keep track of the max size of the canvas */
		int maxX = 0;
		int maxY = 0;

		for(GraphNode n: this.graphNodes.values()) {
			JLabel l = n.getLabel();
			canvasPanel.add(l);		
			
			int curX = n.getLabel().getX()+n.getLabel().getWidth();
			int curY = n.getLabel().getY()+n.getLabel().getHeight();
			
			maxX = Math.max(curX, maxX);
			maxY = Math.max(curY, maxY);
		}

		canvasPanel.setPreferredSize(new Dimension(maxX + 40, maxY + 40));
		canvasPanel.repaint();
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
			canvasPanel.add(err);
			e.printStackTrace();
			return;
		} catch (IOException e) {
			JLabel err = new JLabel("ERROR: Could not read XML");
			canvasPanel.add(err);
			e.printStackTrace();
			return;
		} catch (ParserConfigurationException e) {
			JLabel err = new JLabel("ERROR: XML parse misconfigured");
			canvasPanel.add(err);
			e.printStackTrace();
			return;
		}
		
		try {
			submit = new URL(applet.getCodeBase().toString()
					+ doc.getElementsByTagName("submit").item(0));
		} catch (MalformedURLException e) {
			JLabel err = new JLabel(
					"ERROR: Malformed URL: "+inputURL.toString());
			canvasPanel.add(err);
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
			
			ImageIcon sel_img = createImageIcon(
					n.getElementsByTagName("sel_img").item(0).getTextContent(),
					"Selected Node");

			ImageIcon unsel_img = createImageIcon(
					n.getElementsByTagName("unsel_img").item(0).getTextContent(),
					"Deselected Node");

			ImageIcon err_img = createImageIcon(
					n.getElementsByTagName("err_img").item(0).getTextContent(),
					"Erroroneous Node");
			
			String name = n.getElementsByTagName(
					"name").item(0).getTextContent();
			
			Boolean is_selected = n.getElementsByTagName(
					"is_selected").item(0).getTextContent().equalsIgnoreCase("True");
			
			Boolean has_error = n.getElementsByTagName(
					"has_err").item(0).getTextContent().equalsIgnoreCase("True");
			
			graphNodes.put(id, new GraphNode(id, x, y, sel_img, unsel_img, 
					err_img, name, is_selected, has_error));
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
			GraphNode src = this.graphNodes.get(src_id);
			
			String dst_id = n.getElementsByTagName(
					"dst").item(0).getTextContent();
			GraphNode dst = this.graphNodes.get(dst_id);
			
			Boolean is_selected = n.getElementsByTagName(
					"is_selected").item(0).getTextContent(
							).equalsIgnoreCase("True");
			
			Boolean has_error = n.getElementsByTagName(
					"has_err").item(0).getTextContent(
							).equalsIgnoreCase("True");
			System.err.println("    v1 Done link "+i);
			
			if(src == null) {
				System.err.printf("Link %d missing src id %s\n", i, src_id);
			} else if(dst == null) {
				System.err.printf("Link %d missing dst id %s\n", i, src_id);
			} else {
				System.err.println("    Addin link "+i);
				graphLinks.put(id, new GraphLink(id, src, dst, 
						is_selected, has_error));
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
		for(GraphNode n: this.graphNodes.values()) {
			if(n.isSelected()) {
				v.add(n.getId());
			}
		}
		map.put("node_id", v);
		
		v = new HashSet<String>();
		for(GraphLink l: this.graphLinks.values()) {
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
    	return (String[])getTopoMap().get(key).toArray();
    }

    @Override
	public void actionPerformed(ActionEvent evt) {
		if(evt.getActionCommand().equals(RESERVE_ACTION)) {
			try {
				getOrPost(submit, getTopoMap());
			} catch (MalformedURLException e) {
				JOptionPane.showMessageDialog(
						null,
						"Submit URL is malformed. Error making reservation.",
						"Malformed URL Error",
                        JOptionPane.ERROR_MESSAGE);
				e.printStackTrace();
			} catch (IOException e) {
				JOptionPane.showMessageDialog(
						null,
						"I/O Error making reservation.",
						"I/O Error",
                        JOptionPane.ERROR_MESSAGE);
				e.printStackTrace();
			}
		}
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
