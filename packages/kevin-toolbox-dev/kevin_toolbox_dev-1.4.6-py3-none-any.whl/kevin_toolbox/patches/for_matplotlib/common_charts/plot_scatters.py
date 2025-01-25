import os
import matplotlib.pyplot as plt
from kevin_toolbox.patches.for_matplotlib.color import generate_color_list
from kevin_toolbox.patches.for_os.path import replace_illegal_chars


def plot_scatters(data_s, title, x_name, y_name, cate_name=None, output_dir=None, **kwargs):
    paras = {
        "dpi": 200,
        "scatter_size": 5
    }
    paras.update(kwargs)

    plt.clf()
    #
    color_s = None
    if cate_name is not None:
        cates = list(set(data_s[cate_name]))
        color_s = {i: j for i, j in zip(cates, generate_color_list(nums=len(cates)))}
        c = [color_s[i] for i in data_s[cate_name]]
    else:
        c = "blue"
    # 创建散点图
    plt.scatter(data_s[x_name], data_s[y_name], s=paras["scatter_size"], c=c, alpha=0.8)
    #
    plt.xlabel(f'{x_name}')
    plt.ylabel(f'{y_name}')
    plt.title(f'{title}')
    # 添加图例
    if cate_name is not None:
        plt.legend(handles=[
            plt.Line2D([0], [0], marker='o', color='w', label=i, markerfacecolor=j,
                       markersize=min(paras["scatter_size"], 5)) for i, j in color_s.items()
        ])

    if output_dir is None:
        plt.show()
        return None
    else:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{replace_illegal_chars(title)}.png')
        plt.savefig(output_path, dpi=paras["dpi"])
        return output_path


if __name__ == '__main__':
    data_s_ = dict(
        x=[1, 2, 3, 4, 5],
        y=[2, 4, 6, 8, 10],
        categories=['A', 'B', 'A', 'B', 'A']
    )

    plot_scatters(data_s=data_s_, title='test', x_name='x', y_name='y', cate_name='categories')
