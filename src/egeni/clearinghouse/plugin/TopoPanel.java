import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Dimension;
import java.awt.Insets;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLEncoder;
import java.security.KeyStore.Builder;
import java.util.HashMap;
import java.util.Map;
import java.util.Vector;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JApplet;
import javax.swing.JButton;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import org.w3c.dom.*;
import org.xml.sax.*;

import javax.xml.parsers.*;

public class TopoPanel extends JPanel implements ActionListener {

	private static final long serialVersionUID = -8517569564217332387L;

	private static final String RESET_ACTION = "RESET";
	private static final String RESERVE_ACTION = "RESERVE";
	
	private JPanel canvasPanel;
	private JApplet applet;
	private Map<String, GraphNode> graphNodes;
	private Vector<GraphLink> graphLinks;
	
	public TopoPanel(JApplet applet, URL inputURL) {
		super(new BorderLayout());
		
		this.graphNodes = new HashMap<String, GraphNode>();
		this.graphLinks = new Vector<GraphLink>();
		
		this.applet = applet;
		
		canvasPanel = new JPanel();
		canvasPanel.setBackground(Color.white);
		JScrollPane sPane = new JScrollPane(canvasPanel);
		this.add(sPane, BorderLayout.CENTER);

		parseInputXML(inputURL);
		drawTopo();
				
		JPanel bottomPanel = new JPanel();
		
		JButton reserveButton = new JButton("Reserve");
		JButton resetButton = new JButton("Reset");
		
		bottomPanel.add(reserveButton);
		bottomPanel.add(resetButton);
		this.add(bottomPanel, BorderLayout.SOUTH);
		
		reserveButton.setActionCommand(RESERVE_ACTION);
		resetButton.setActionCommand(RESET_ACTION);
		
		reserveButton.addActionListener(this);
		resetButton.addActionListener(this);
	}

	/**
	 * Draw the topology into the canvas
	 */
    private void drawTopo() {
		this.canvasPanel.setLayout(null);

		for(GraphNode n: this.graphNodes.values()) {
			Icon img = 
			if(n.isSelected()) {
				if(n.hasError()) {
					
				}
			}
				
		canvasPanel.add(l);		
		Insets insets = canvasPanel.getInsets();
		l.setBounds(20+insets.left,20+insets.top, i.getIconWidth(), i.getIconHeight());
		
		canvasPanel.setPreferredSize(new Dimension(300, 300));
	}

	private void parseInputXML(URL inputURL) {
    	/* Get the XML from the url in the parameters */
    	InputStream in = null;
    	try {
			in = this.getOrPost(inputURL, null);
		} catch (MalformedURLException e) {
			JLabel err = new JLabel(
					"ERROR: Malformed URL: "+inputURL.toString());
			canvasPanel.add(err);
			e.printStackTrace();
			return;
		} catch (IOException e) {
			JLabel err = new JLabel("ERROR: Could not read from URL: "
					+inputURL.toString());
			canvasPanel.add(err);
			e.printStackTrace();
			return;
		}
    	
		Document doc = null;
		try {
			DocumentBuilderFactory factory = 
				DocumentBuilderFactory.newInstance();
			DocumentBuilder builder = factory.newDocumentBuilder();
			doc = builder.parse(in);
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

		NodeList nodes = doc.getElementsByTagName("node");
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
			
			Icon sel_img = createImageIcon(
					n.getElementsByTagName("sel_img").item(0).getTextContent(),
					"Selected Node");

			Icon unsel_img = createImageIcon(
					n.getElementsByTagName("unsel_img").item(0).getTextContent(),
					"Deselected Node");

			Icon err_img = createImageIcon(
					n.getElementsByTagName("err_img").item(0).getTextContent(),
					"Erroroneous Node");
			
			String name = n.getElementsByTagName(
					"name").item(0).getTextContent();
			
			Boolean is_selected = n.getElementsByTagName(
					"is_selected").item(0).getTextContent().equalsIgnoreCase("True");
			
			Boolean has_error = n.getElementsByTagName(
					"has_error").item(0).getTextContent().equalsIgnoreCase("True");
			
			graphNodes.put(id, new GraphNode(id, x, y, sel_img, unsel_img, 
					err_img, name, is_selected, has_error));
		}
		
		NodeList links = doc.getElementsByTagName("link");
		for(int i=0; i<links.getLength(); i++) {
			Element n = (Element) links.item(i);
			
			String id = 
				n.getElementsByTagName(
						"id").item(0).getTextContent();
			
			Element srcElem = (Element) n.getElementsByTagName(
					"src").item(0);
			String src_id = srcElem.getElementsByTagName(
					"node_id").item(0).getTextContent();
			GraphNode src = this.graphNodes.get(src_id);
			
			Element dstElem = (Element) n.getElementsByTagName(
					"dst").item(0);
			String dst_id = dstElem.getElementsByTagName(
					"node_id").item(0).getTextContent();
			GraphNode dst = this.graphNodes.get(dst_id);
			
			Boolean is_selected = n.getElementsByTagName(
					"is_selected").item(0).getTextContent(
							).equalsIgnoreCase("True");
			
			Boolean has_error = n.getElementsByTagName(
					"has_error").item(0).getTextContent(
							).equalsIgnoreCase("True");
			
			graphLinks.add(new GraphLink(id, src, dst, 
					is_selected, has_error));
		}
	}

	/** Returns an ImageIcon, or null if the path was invalid. */
    protected ImageIcon createImageIcon(String path,
    		String description) {
        java.net.URL imgURL = getClass().getResource(path);
        if (imgURL != null) {
            return new ImageIcon(imgURL, description);
        } else {
            System.err.println("Couldn't find file: " + path);
            return null;
        }
    }

	@Override
	public void actionPerformed(ActionEvent evt) {
		if(evt.getActionCommand().equals(RESERVE_ACTION)) {
			
		}
	}
	
	private InputStream getOrPost(
			final URL url,
			final Map<String, String> params) 
	throws MalformedURLException, IOException {
		Boolean doOutput = params != null;
		StringBuffer paramsAsString = null;
		if(doOutput) {
			paramsAsString = new StringBuffer("");
			for(String k: params.keySet()) {
				if(paramsAsString.length()>0){
					paramsAsString.append("&");
				}
				paramsAsString.append(k+"="+params.get(k));
			}
		}
		//String outStr = URLEncoder.encode(paramsAsString.toString(), "UTF-8");
		
		// send parameters to server
		URLConnection con = url.openConnection();
		con.setDoOutput(doOutput);
		con.setDoInput(true);
		
		if(doOutput) {
			con.setRequestProperty("Content=length", String
					.valueOf(paramsAsString.length()));
			
			OutputStreamWriter out = new OutputStreamWriter(
					con.getOutputStream());
			out.write(paramsAsString.toString());
			out.close();
		}
		
		return con.getInputStream();
	}
}
