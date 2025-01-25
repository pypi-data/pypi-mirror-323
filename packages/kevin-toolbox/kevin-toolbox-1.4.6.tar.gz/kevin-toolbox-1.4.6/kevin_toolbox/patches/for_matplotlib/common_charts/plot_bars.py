import os
import copy
from kevin_toolbox.computer_science.algorithm import for_seq
import matplotlib.pyplot as plt
from kevin_toolbox.patches.for_os.path import replace_illegal_chars

# TODO 在 linux 系统下遇到中文时，尝试自动下载中文字体，并尝试自动设置字体
# font_path = os.path.join(root_dir, "utils/SimHei.ttf")
# font_name = FontProperties(fname=font_path)


def plot_bars(data_s, title, x_name, y_label=None, output_dir=None, **kwargs):
    data_s = copy.deepcopy(data_s)
    paras = {
        "dpi": 200
    }
    paras.update(kwargs)

    plt.clf()
    #
    x_all_ls = data_s.pop(x_name)
    #
    for i, (k, y_ls) in enumerate(data_s.items()):
        if i == 0:
            plt.bar([j - 0.1 for j in range(len(x_all_ls))], y_ls, width=0.2, align='center', label=k)
        else:
            plt.bar([j + 0.1 for j in range(len(x_all_ls))], y_ls, width=0.2, align='center', label=k)

    plt.xlabel(f'{x_name}')
    plt.ylabel(f'{y_label if y_label else "value"}')
    temp = for_seq.flatten_list([list(i) for i in data_s.values()])
    y_min, y_max = min(temp), max(temp)
    plt.ylim(max(min(y_min, 0), y_min - (y_max - y_min) * 0.2), y_max + (y_max - y_min) * 0.1)
    plt.xticks(list(range(len(x_all_ls))), labels=x_all_ls)  # , fontproperties=font_name
    plt.title(f'{title}')
    # 显示图例
    plt.legend()

    if output_dir is None:
        plt.show()
        return None
    else:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{replace_illegal_chars(title)}.png')
        plt.savefig(output_path, dpi=paras["dpi"])
        return output_path


if __name__ == '__main__':
    plot_bars(data_s={
        'a': [1.5, 2, 3, 4, 5],
        'b': [5, 4, 3, 2, 1],
        'c': [1, 2, 3, 4, 5]},
        title='test', x_name='a', output_dir=os.path.join(os.path.dirname(__file__), "temp"))
