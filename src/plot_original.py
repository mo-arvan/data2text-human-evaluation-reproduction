import pandas as pd
import seaborn as sns


original_df = pd.read_csv("original/results.csv")


original_df.drop(columns=["#Supp", "#Contra"], inplace=True)

sub_df = original_df.melt(id_vars='System', var_name='Measure', value_name='Best-Worst Scale')
color_palette = sns.color_palette("colorblind", 5)
# swap first and second colors, we want to the gold label to have the same color
color_palette[0], color_palette[1] = color_palette[1], color_palette[0]
metric_column = "Best-Worst Scale"
ax = sns.barplot(data=sub_df,
                 x='Measure',
                 y='Best-Worst Scale',
                 hue='System',
                 palette=color_palette,
                 # ax=axes_list[plot_index]
                 )
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
# plt.legend(bbox_to_anchor=(1.0, 1), loc='upper left', borderaxespad=0)
ax.set(xlabel='', ylabel=metric_column)
ax.set_ylim([min_value, max_value])
plot_title = response
if filter_name != "None":
    plot_title += " - " + filter_name
ax.set_title(plot_title)
# compact the layout
plt.tight_layout()

for i in ax.containers:
    ax.bar_label(i, )

save_path = "results/figures/" + get_file_name(
    response + " " + metric_column + " " + filter_name) + ".pdf"
plt.savefig(save_path)
plt.clf()