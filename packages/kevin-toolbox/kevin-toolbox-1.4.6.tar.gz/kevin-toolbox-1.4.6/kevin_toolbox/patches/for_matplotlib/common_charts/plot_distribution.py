import os
import math
import matplotlib.pyplot as plt
import numpy as np
from kevin_toolbox.patches.for_os.path import replace_illegal_chars


def plot_distribution(data_s, title, x_name=None, x_name_ls=None, type_="hist", output_dir=None, **kwargs):
    paras = {
        "dpi": 200
    }
    paras.update(kwargs)
    if x_name is not None:
        x_name_ls = [x_name, ]
    assert isinstance(x_name_ls, (list, tuple)) and len(x_name_ls) > 0

    plt.clf()

    alpha = max(1 / len(x_name_ls), 0.3)
    # 检查数据类型
    if type_ in ["histogram", "hist"]:
        # 数字数据，绘制概率分布图
        for x_name in x_name_ls:
            data = data_s[x_name]
            assert all(isinstance(x, (int, float)) for x in data), \
                f'输入数组中的元素类型不一致'
            if "steps" in paras:
                min_ = math.floor(min(data) / paras["steps"]) * paras["steps"]
                max_ = math.ceil(max(data) / paras["steps"]) * paras["steps"]
                bins = np.arange(min_, max_ + paras["steps"], paras["steps"])
            else:
                bins = np.linspace(paras.get("min", min(data)), paras.get("max", max(data)), paras["bin_nums"] + 1)
            plt.hist(data, density=True, bins=bins, alpha=alpha, label=x_name)
    elif type_ in ["category", "cate"]:
        # 字符串数据，绘制概率直方图
        for x_name in x_name_ls:
            data = data_s[x_name]
            unique_values, counts = np.unique(data, return_counts=True)
            probabilities = counts / len(data)
            plt.bar([f'{i}' for i in unique_values], probabilities, label=x_name, alpha=alpha)
    else:
        raise ValueError(f'unsupported plot type {type_}')

    plt.xlabel(f'value')
    plt.ylabel('prob')
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
    plot_distribution(data_s={
        'a': [1, 2, 3, 4, 5, 3, 2, 1],
        'c': [1, 2, 3, 4, 5, 0, 0, 0]},
        title='test', x_name_ls=['a', 'c'], type_="category",
        output_dir=os.path.join(os.path.dirname(__file__), "temp"))
