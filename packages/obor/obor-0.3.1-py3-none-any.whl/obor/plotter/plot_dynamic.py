import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def plot_dynamic(data: dict, x_values: list, title: str, x_label: str = "X Values", y_label: str = "Y Values"):
    """
    Plots dynamic lines based on the input dictionary, with a specified x_values array for the x-axis.
    Assigns the same marker to keys with the same prefix.

    Args:
        data (dict): A dictionary where keys are line names and values are 1D arrays.
                     Example:
                     {
                         "low_magnitude-acc": [0.92, 0.91, ...],
                         "low_magnitude-f1": [0.92, 0.91, ...],
                         "bbs-acc": [0.92, 0.91, ...],
                         "bbs-f1": [0.92, 0.91, ...]
                     }
        x_values (list): A 1D array to use as the x-axis values. All arrays in `data` must have the same length as this array.
        title (str): Title of the plot. Default is "Y Values vs X Values".
        x_label (str): Label for the x-axis. Default is "X Values".
        y_label (str): Label for the y-axis. Default is "Y Values".
    """
    title = f"{y_label} vs {x_label}" if title == "" else title

    # Validate that all arrays in the dictionary have the same length as the x_values array
    x_values_length = len(x_values)
    for key, values in data.items():
        if len(values) != x_values_length:
            raise ValueError(f"Length of array '{key}' does not match the length of the x_values array. "
                             f"Expected: {x_values_length}, Found: {len(values)}")

    # Check if Arial font is available
    if 'Arial' in [f.name for f in fm.fontManager.ttflist]:
        plt.rcParams['font.family'] = 'Arial'  # Use Arial if available
    else:
        plt.rcParams['font.family'] = 'sans-serif'  # Fallback to default sans-serif font
    plt.rcParams['font.size'] = 11  

    # Create a figure
    plt.figure(figsize=(8, 6))

    # Define a list of markers to cycle through
    markers = ['o', 'x', 'X', '^', 'v', '<', '>', 'p', '*', 'h', 'H', '+', 's', 'd', 'D', '|', '_']

    # Create a dictionary to track marker usage for each prefix
    prefix_marker_map = {}

    # Iterate over the dictionary and plot each line with a unique marker based on prefix
    for key, values in data.items():
        # Extract the prefix (assumes prefix is before the first hyphen)
        prefix = key.split('-')[0]

        # Assign a marker to the prefix if not already assigned
        if prefix not in prefix_marker_map:
            # Use the next marker in the list, cycling back to the start if necessary
            prefix_marker_map[prefix] = markers[len(prefix_marker_map) % len(markers)]

        # Plot the line with the assigned marker
        plt.plot(x_values, values, label=key, linewidth=0.8, marker=prefix_marker_map[prefix])

    # Add labels, title, and legend
    plt.title(title, fontsize=11, weight='bold')
    plt.xlabel(x_label, fontsize=11)
    plt.ylabel(y_label, fontsize=11)
    plt.legend(fontsize=11)
    plt.grid(visible=True, linestyle='--', alpha=0.6)

    # Adjust layout and show the plot
    plt.tight_layout(pad=4)
    plt.show()