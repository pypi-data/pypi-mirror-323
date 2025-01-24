import contextlib
import os
import re
from io import BytesIO
from urllib.parse import unquote

import pandas as pd
import numpy as np
import warnings
from requests import request
"""
用于excel校验
"""
warnings.simplefilter("ignore")


def read_excel_from_oss(url="", method="get"):
    """读取oss的excel内容并写入到本地csv"""
    try:
        result = request(method=method, url=url)
        excel_data = BytesIO(result.content)
        print(f"成功读取oss文件内容: {url}")
        return excel_data
    except Exception as e:
        print(f"读取oss报错 {url} 时出错：{e}")


def read_excel_and_write_to_dict(excel_data=None, file_name=None):
    """excel内容并写入到内存dict中
    :param excel_data：excel的io对象, 参数和file_name互斥
    :file_name: excel文件名称，目前读取check_file目录下文件，参数和excel_data互斥
    """
    try:
        if excel_data is not None and file_name is not None:
            pass
        elif file_name is not None:
            excel_data = os.path.join(os.path.dirname(os.getcwd()) + "/check_file/" + file_name)
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module=re.escape('openpyxl.styles.stylesheet'))
            df = pd.read_excel(excel_data, engine="openpyxl")
        # 将DataFrame转换为字典，以行为单位存储数据
        row_dict = {}  # 创建一个空字典来存储按行转换的数据
        for index, row in df.iterrows():  # 遍历DataFrame中的每一行
            row_dict[index] = row.to_dict()  # 将每一行转换为字典并存储在row_dict中
        return row_dict
    except Exception as e:
        print(f"excel写入dict时出错：{e}")


def read_excel_and_write_to_list(excel_data=None, file_name=None):
    """excel内容并写入到内存list中
    :param excel_data：excel的io对象, 参数和file_name互斥
    :file_name: excel文件名称，目前读取check_file目录下文件，参数和excel_data互斥

    io：可以是文件路径、文件对象或 ExcelFile 对象，代表要读取的 Excel 文件。
    sheet_name：指定要读取的工作表，默认为第一个工作表（索引为 0）。
    header：指定哪一行作为列名，默认为第一行（索引为 0）。
    names：可以为列提供自定义名称，如果设置了这个，会覆盖文件中的列名。
    index_col：可以指定某一列或多列作为索引。
    usecols：可以指定要读取的列，可以是列的索引、列名或一个筛选函数。
    dtype：可以指定数据类型，控制数据的类型转换。
    engine：指定使用的 Excel 引擎，比如 xlrd、openpyxl 等。
    converters：可以为不同的列指定自定义的转换函数，以字典形式存储。
    true_values 和 false_values：定义哪些值会被视为 True 或 False。
    skiprows：可以指定要跳过的行，可以是一个整数序列、一个整数或一个函数。
    nrows：可以指定要读取的行数。
    na_values：可以指定哪些值会被视为 NaN。
    keep_default_na：决定是否使用默认的 NaN 值。
    na_filter：决定是否过滤 NaN 值。
    verbose：决定是否输出详细信息。
    parse_dates：决定是否解析日期，可以是一个列表、字典或布尔值。
    date_parser：自定义的日期解析函数。
    date_format：日期的格式设置。
    thousands：千位分隔符。
    decimal：小数点分隔符。
    comment：注释字符，以该字符开头的行将被跳过。
    skipfooter：指定要跳过的文件末尾的行数。
    storage_options：存储选项。
    dtype_backend：数据类型后端。
    engine_kwargs：传递给引擎的额外参数。


    """
    try:
        if excel_data is not None and file_name is not None:
            pass
        elif file_name is not None:
            excel_data = os.path.join(os.path.dirname(os.getcwd()) + "/check_file/" + file_name)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module=re.escape('openpyxl.styles.stylesheet'))
            df = pd.read_excel(excel_data, engine="openpyxl")
        # 将DataFrame转换为字典，以行为单位存储数据
        rows_list = df.values.tolist()
        return rows_list
    except Exception as e:
        print(f"excel写入list时出错：{e}")


def read_excel_and_write_to_csv(excel_data, file_name):
    """excel内容并写入到csv中"""
    try:
        df = pd.read_excel(excel_data, engine="openpyxl")
        local_csv_path = os.path.join(os.path.dirname(os.getcwd()) + "/temp_file/" + file_name)
        df.to_csv(local_csv_path, index=False)
        return local_csv_path
    except Exception as e:
        print(f"excel写入csv时出错：{e}")


def check_excel(check_type="content", **kwargs):
    """对比excel
    :param: type: 需要对比类型，
            枚举：content：对比两表格内容
                方式1：传参actual_oss和expected_oss，参数类型str,url
                放松1：传参actual和expected，参数类型list or dict
            excelName: 对比两表格文件名称
            all: 对比所有内容
    """
    try:
        if check_type == "content":
            if "actual" in kwargs.keys() and "expected" in kwargs.keys():
                return check_excel_content(actual=kwargs["actual"], expected=kwargs["expected"])
            else:
                return check_excel_content(actual=read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["actual_oss"])),
                                           expected=read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["expected_oss"]))
                                           )
        elif check_type == "excelName":
            return check_excel_name(actual_oss=kwargs["actual_oss"], expected_oss=kwargs["expected_oss"])
        elif check_type == "all":
            actual_content = read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["actual_oss"]))
            expected_content = read_excel_and_write_to_list(excel_data=read_excel_from_oss(url=kwargs["expected_oss"]))
            flag1, content_result = check_excel_content(actual=actual_content, expected=expected_content)
            flag2, name_result = check_excel_name(actual_oss=kwargs["actual_oss"], expected_oss=kwargs["expected_oss"])
            return flag1 and flag2, {"文件名称": name_result, "导出内容": content_result}
        else:
            return False, f"不支持此类型: {check_type}"
    except Exception as e:
        print(f"对比excel异常：{e}")
        return False, [e]


def check_excel_name(actual_oss, expected_oss):
    """校验excel文件名称
    :param actual_oss:实际oss链接
    :param actual_oss:预期oss链接
    """
    try:
        actual_name = unquote(actual_oss.split("/")[-1])
        expected_name = unquote(expected_oss.split("/")[-1])
        if actual_name == expected_name:
            return True, "excel文件名称-匹配"
        else:
            return False, f"excel文件名称-不匹配, 实际: {actual_name}, 预期: {expected_name}"
    except BaseException as msg:
        return False, f"excel文件名称-服务异常: {msg}"


def check_excel_content(actual, expected):
    """校验excel内容
       :param actual: 实际内容，list或dict类型
       :param expected:预期内容：list或dict类型
     """
    try:
        if actual == expected:
            return True, ["excel内容-完全匹配"]
        else:
            errors = []
            # 断言1：校验行数
            actual_num = len(actual)
            expected_num = len(expected)
            check_row = actual_num - expected_num
            if check_row == 0:
                errors.append("excel内容-预期和实际行数相等，为" + str(actual_num) + "行")
            else:
                errors.append(
                    "excel内容-行数和预期对比差" + check_row.__str__() + "行" + ", 实际:" + str(actual_num) + "预期: " + str(
                        expected_num))
            # 断言不匹配行
            if check_row >= 0:
                num = len(expected)
            else:
                num = len(actual)
            for i in range(num):
                if actual[i] == expected[i]:
                    continue
                else:
                    errors.append(
                        "excel内容-第" + str(i + 1) + "行不匹配，预期为：" + str(expected[i]) + ", 实际为: " + str(actual[i]))
            return False, errors
    except Exception as e:
        print(f"excel内容-服务异常：{e}")
        return False, [e]


def del_temp_file(file_name=""):
    """删除temp下临时文件"""
    file_path = os.path.join(os.path.dirname(os.getcwd()) + "/temp_file/" + file_name)
    try:
        os.remove(file_path)
        print(f"文件 {file_path} 已成功删除。")
    except FileNotFoundError:
        print(f"文件 {file_path} 不存在。")
    except Exception as e:
        print(f"删除文件 {file_path} 时出错：{e}")
