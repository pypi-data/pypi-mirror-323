import requests

from smartpush.export.basic import ExcelExportChecker

if __name__ == '__main__':

    ossurl1 = "https://sl-smartfile.oss-ap-southeast-1.aliyuncs.com/material_ec2/2025-01-16/8556e34c8d4d45f0bb2d42dc8871a90b/%E8%A1%A8%E5%8D%95%E4%BB%BB%E5%8A%A1%E6%95%B0%E6%8D%AE%E6%A6%82%E8%A7%88.xlsx"
    ossurl2 = "https://sl-smartfile.oss-ap-southeast-1.aliyuncs.com/material_ec2/2025-01-16/8556e34c8d4d45f0bb2d42dc8871a90b/%E8%A1%A8%E5%8D%95%E4%BB%BB%E5%8A%A1%E6%95%B0%E6%8D%AE%E6%A6%82%E8%A7%88.xlsx"

    a = ExcelExportChecker.read_excel_and_write_to_list(excel_data=ExcelExportChecker.read_excel_from_oss(url=ossurl1))
    b = ExcelExportChecker.read_excel_and_write_to_list(excel_data=ExcelExportChecker.read_excel_from_oss(url=ossurl2))
    print(ExcelExportChecker.check_excel(actual=a, expected=b))
    # print(ExcelExportChecker.check_excel_name(actual_oss=ossurl1, expected_oss=ossurl2))
