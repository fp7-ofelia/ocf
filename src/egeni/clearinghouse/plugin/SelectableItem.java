/**
 * 
 */
package egeni.clearinghouse.plugin;

/**
 * @author jnaous
 *
 */
public interface SelectableItem {
	public Boolean isSelected();
	public void setSelected(Boolean isSelected);
	public void toggleSelected();
}
