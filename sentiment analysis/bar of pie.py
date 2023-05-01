import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import numpy as np

hatered=float(input())
pleasent=float(input())
neutral=float(input())
hateful=float(input())
offending=float(input())
violent=float(input())
action_needed=float(input())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 5))
fig.subplots_adjust(wspace=0)


overall_ratios = [hatered, pleasent, neutral]
labels = ['Hatred', 'pleasent', 'Neutral']
explode = [0.1, 0, 0]
colors = ['#F44336', '#4CAF50', '#9E9E9E'] # color for each wedge

angle = -180 * overall_ratios[0]
wedges, *_ = ax1.pie(overall_ratios, autopct='%1.1f%%', startangle=angle,
labels=labels, explode=explode, colors=colors) # set the colors of the wedges


# bar chart parameters
age_ratios = [action_needed, violent, offending, hateful]
age_labels = ['Action Needed', 'Violent', 'Offending', 'Hateful']
bottom = 1
width = .2

# Adding from the top matches the legend.
for j, (height, label) in enumerate(reversed([*zip(age_ratios, age_labels)])):
    bottom -= height
    bc = ax2.bar(0, height, width, bottom=bottom, color='C3', label=label,
                 alpha=0.1 + 0.25 * j)
    ax2.bar_label(bc, labels=[f"{height:.0%}"], label_type='center')

ax2.set_title('Percentage of Hatred')
ax2.legend()
ax2.axis('off')
ax2.set_xlim(- 2.5 * width, 2.5 * width)

# use ConnectionPatch to draw lines between the two plots
theta1, theta2 = wedges[0].theta1, wedges[0].theta2
center, r = wedges[0].center, wedges[0].r
bar_height = sum(age_ratios)

# draw top connecting line
x = r * np.cos(np.pi / 180 * theta2) + center[0]
y = r * np.sin(np.pi / 180 * theta2) + center[1]
con = ConnectionPatch(xyA=(-width / 2, bar_height), coordsA=ax2.transData,
                      xyB=(x, y), coordsB=ax1.transData)
con.set_color([0.5, 0.5, 0.5])  # change color to gray
con.set_linewidth(4)
ax2.add_artist(con)

# draw bottom connecting line
x = r * np.cos(np.pi / 180 * theta1) + center[0]
y = r * np.sin(np.pi / 180 * theta1) + center[1]
con = ConnectionPatch(xyA=(-width / 2, 0), coordsA=ax2.transData,
                      xyB=(x, y), coordsB=ax1.transData)
con.set_color([0.5, 0.5, 0.5])  # change color to gray
ax2.add_artist(con)
con.set_linewidth(4)

plt.show()
