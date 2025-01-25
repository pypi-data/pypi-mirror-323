import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from kevin_toolbox.patches.for_matplotlib.color import generate_color_list
from kevin_toolbox.patches.for_os.path import replace_illegal_chars


def plot_scatters_matrix(data_s, title, x_name_ls, cate_name=None, output_dir=None, cate_color_s=None, **kwargs):
    paras = {
        "dpi": 200,
        "diag_kind": "kde"  # 设置对角线图直方图/密度图 {‘hist’, ‘kde’}
    }
    assert cate_name in data_s and len(set(x_name_ls).difference(set(data_s.keys()))) == 0
    if cate_color_s is None:
        temp = set(data_s[cate_name])
        cate_color_s = {k: v for k, v in zip(temp, generate_color_list(len(temp)))}
    assert set(cate_color_s.keys()) == set(data_s[cate_name])
    paras.update(kwargs)

    plt.clf()
    # 使用seaborn绘制散点图矩阵
    sns.pairplot(
        pd.DataFrame(data_s),
        diag_kind=paras["diag_kind"],  # 设置对角线图直方图/密度图 {‘hist’, ‘kde’}
        hue=cate_name,  # hue 表示根据该列的值进行分类
        palette=cate_color_s, x_vars=x_name_ls, y_vars=x_name_ls,  # x_vars，y_vars 指定子图的排列顺序
    )
    #
    plt.subplots_adjust(top=0.95)
    plt.suptitle(f'{title}', y=0.98, x=0.47)
    # g.fig.suptitle(f'{title}', y=1.05)

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
        z=[2, 4, 6, 8, 10],
        categories=['A', 'B', 'A', 'B', 'A'],
        title='test',
    )

    plot_scatters_matrix(data_s=data_s_, title='test', x_name_ls=['y', 'x', 'z'], cate_name='categories',
                         cate_color_s={'A': 'red', 'B': 'blue'})
