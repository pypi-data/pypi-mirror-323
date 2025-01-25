import os
import copy
import matplotlib.pyplot as plt
from kevin_toolbox.patches.for_os.path import replace_illegal_chars
from kevin_toolbox.patches.for_matplotlib.color import generate_color_list


def plot_lines(data_s, title, x_name, output_dir=None, **kwargs):
    data_s = copy.copy(data_s)
    line_nums = len(data_s) - 1
    paras = {
        "dpi": 200,
        "color_ls": generate_color_list(nums=line_nums),
        "marker_ls": None,
        "linestyle_ls": '-',
    }
    paras.update(kwargs)
    for k, v in paras.items():
        if k.endswith("_ls") and not isinstance(v, (list, tuple)):
            paras[k] = [v] * line_nums
    assert line_nums == len(paras["color_ls"]) == len(paras["marker_ls"]) == len(paras["linestyle_ls"])

    plt.clf()
    #
    x_all_ls = data_s.pop(x_name)
    data_s, temp = dict(), data_s
    for k, v_ls in temp.items():
        y_ls, x_ls = [], []
        for x, v in zip(x_all_ls, v_ls):
            if x is None or v is None:
                continue
            x_ls.append(x)
            y_ls.append(v)
        if len(x_ls) == 0:
            continue
        data_s[k] = (x_ls, y_ls)
    #
    for i, (k, (x_ls, y_ls)) in enumerate(data_s.items()):
        plt.plot(x_ls, y_ls, label=f'{k}', color=paras["color_ls"][i], marker=paras["marker_ls"][i],
                 linestyle=paras["linestyle_ls"][i])
    plt.xlabel(f'{x_name}')
    plt.ylabel('value')
    plt.title(f'{title}')
    # 显示图例
    plt.legend()

    if output_dir is None:
        plt.show()
        return None
    else:
        # 对非法字符进行替换
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f'{replace_illegal_chars(title)}.png')
        plt.savefig(output_path, dpi=paras["dpi"])
        return output_path


if __name__ == '__main__':
    plot_lines(data_s={
        'a': [1, 2, 3, 4, 5],
        'b': [5, 4, 3, 2, 1],
        'c': [1, 2, 3, 4, 5]},
        title='test', x_name='a', output_dir=os.path.join(os.path.dirname(__file__), "temp"))
