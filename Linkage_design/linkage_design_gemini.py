import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

def get_circle_intersection(p1, r1, p2, r2):
    """
    Finds the intersection of two circles (the elbow of the linkage).
    Returns the solution corresponding to the 'open' assembly configuration.
    """
    d = np.linalg.norm(p2 - p1)
    
    if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
        return None 

    a = (r1**2 - r2**2 + d**2) / (2 * d)
    h = np.sqrt(max(0, r1**2 - a**2))
    
    x2 = p1[0] + a * (p2[0] - p1[0]) / d
    y2 = p1[1] + a * (p2[1] - p1[1]) / d
    
    # We choose the 'elbow-up' configuration (positive h for y-component)
    # This might need adjustment based on initial linkage geometry
    x3_1 = x2 + h * (p2[1] - p1[1]) / d
    y3_1 = y2 - h * (p2[0] - p1[0]) / d
    
    return np.array([x3_1, y3_1])

# --- 1. SYSTEM CONFIGURATION (Tunable) ---
# Lengths (Units are arbitrary, e.g., inches or mm)
L_g = 4.0   # Ground Link (dist between pivots)
L_1 = 1.0   # Crank (Input)
L_2 = 4.0   # Coupler
L_3 = 3.0   # Rocker (Follower)

# Coupler Point Geometry (Triangle shape on the coupler link)
coupler_u = 2.0 
coupler_v = 1.5 

# Output Stage (The Dwell Mechanism)
L_5 = 3.8   # Connecting Rod to Slider
slider_y = -1.0 # Vertical offset of the slider rail

# --- 2. SETUP FOR ANIMATION ---
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_title("Six-Bar Dwell Linkage Animation")
ax.set_xlabel("X-position")
ax.set_ylabel("Y-position")
ax.grid(True)
ax.set_aspect('equal', adjustable='box')

# Set limits based on expected maximum extents of the mechanism
max_x = L_g + L_3 + L_5 + L_1 # Rough estimate
min_x = -L_1 - L_5 - L_3
max_y = L_1 + L_2 + coupler_v # Rough estimate
min_y = slider_y - 0.5

ax.set_xlim(min_x, max_x) 
ax.set_ylim(min_y, max_y)

# Initialize lines for the linkage
# Ground pivots
ground_pivot = np.array([L_g, 0])
input_pivot = np.array([0, 0])

# Drawing elements
link1_line, = ax.plot([], [], 'o-', lw=2, color='blue', label='Crank (Input)')
link2_line, = ax.plot([], [], 'o-', lw=2, color='green', label='Coupler')
link3_line, = ax.plot([], [], 'o-', lw=2, color='purple', label='Rocker')
link5_line, = ax.plot([], [], 'o-', lw=2, color='red', label='Slider Link')
slider_rect = plt.Rectangle((0, slider_y - 0.25), 1.0, 0.5, fc='gray', ec='black') # Slider block
ax.add_patch(slider_rect)

# Fixed points and slider rail
ax.plot([0, L_g], [0, 0], 'ko', markersize=8, label='Fixed Pivots')
ax.plot([min_x, max_x], [slider_y, slider_y], 'k--', alpha=0.5, label='Slider Rail')
coupler_path_line, = ax.plot([], [], 'b:', alpha=0.6, label='Coupler Point Path')

# Text to display current angle
angle_text = ax.text(0.02, 0.95, '', transform=ax.transAxes)

# Store coupler path points
coupler_path_x = []
coupler_path_y = []

# --- Animation function ---
def animate(frame):
    theta = np.radians(frame) # Input crank angle
    
    # A. Input Crank Position
    crank_tip = np.array([L_1 * np.cos(theta), L_1 * np.sin(theta)])
    
    # B. Solve 4-Bar (Find Rocker Tip)
    rocker_tip = get_circle_intersection(crank_tip, L_2, ground_pivot, L_3)
    
    if rocker_tip is None:
        # Handle cases where linkage cannot be formed (should not happen with good design)
        return [] 

    # C. Calculate Coupler Point Position
    vec_coupler = rocker_tip - crank_tip
    len_coupler = np.linalg.norm(vec_coupler)
    uv_vec = vec_coupler / len_coupler
    perp_vec = np.array([-uv_vec[1], uv_vec[0]])
    
    P = crank_tip + (uv_vec * coupler_u) + (perp_vec * coupler_v)
    
    coupler_path_x.append(P[0])
    coupler_path_y.append(P[1])

    # D. Solve Slider Position
    dy = P[1] - slider_y
    if abs(dy) <= L_5:
        dx = np.sqrt(L_5**2 - dy**2)
        # Choose the left-most or right-most point based on desired configuration
        slider_x_pos = P[0] - dx # Assuming slider is generally to the left of P for the dwell
    else:
        # If the coupler point is too far from the slider rail, the link would be too short
        # This means the mechanism has likely "broken" or is not designed correctly for the full range.
        slider_x_pos = P[0] # Default, but indicates an issue

    # Update linkage lines
    link1_line.set_data([input_pivot[0], crank_tip[0]], [input_pivot[1], crank_tip[1]])
    link2_line.set_data([crank_tip[0], rocker_tip[0]], [crank_tip[1], rocker_tip[1]])
    link3_line.set_data([rocker_tip[0], ground_pivot[0]], [rocker_tip[1], ground_pivot[1]])
    link5_line.set_data([P[0], slider_x_pos], [P[1], slider_y])

    # Update slider rectangle position
    slider_rect.set_x(slider_x_pos - slider_rect.get_width()/2) # Center the slider rect

    # Update coupler path
    coupler_path_line.set_data(coupler_path_x, coupler_path_y)

    # Update angle text
    angle_text.set_text(f'Crank Angle: {frame}°')
    
    return link1_line, link2_line, link3_line, link5_line, slider_rect, coupler_path_line, angle_text

# Create the animation
ani = FuncAnimation(fig, animate, frames=np.arange(0, 360, 2), # 2-degree increments for smoother animation
                    interval=50, blit=True, repeat=True)

ax.legend()
plt.show()

# To save the animation as a GIF or MP4, uncomment and run one of these:
# ani.save('six_bar_dwell_linkage.gif', writer='pillow', fps=20)
# ani.save('six_bar_dwell_linkage.mp4', writer='ffmpeg', fps=20)