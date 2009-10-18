
public class GraphLink {
	private String id;
	private GraphNode src;
	private GraphNode dst;
	private Boolean is_selected;
	private Boolean has_error;
	
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
	}

	public GraphNode getDst() {
		return dst;
	}

	public void setDst(GraphNode dst) {
		this.dst = dst;
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
	}
}
